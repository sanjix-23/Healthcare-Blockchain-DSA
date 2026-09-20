"""
Encounter Management and Cryptographic Integrity Verification Endpoints.
Implements the core SHA-256 -> Merkle Tree -> Blockchain anchoring & proof verification pipeline.
"""

import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query, status
from core.crypto import sha256_hash, canonical_json
from core.merkle_tree import MerkleTree
from db.database import get_connection, log_audit, get_canonical_encounter_package
from backend.state import AppState
from backend.models import (
    EncounterCreateRequest,
    EncounterCreateResponse,
    VerificationResponse
)

router = APIRouter(prefix="/api/encounters", tags=["Encounters & Integrity Verification"])


@router.post("", response_model=EncounterCreateResponse, status_code=status.HTTP_201_CREATED)
def create_and_anchor_encounter(req: EncounterCreateRequest):
    """
    Creates a new medical encounter for an existing or newly registered patient.
    
    Cryptographic Pipeline:
    1. Persists off-chain clinical and billing data to SQLite.
    2. Builds canonical EHR JSON package.
    3. Computes SHA-256 fingerprint: record_hash = SHA-256(canonical_json).
    4. Constructs binary Merkle Tree from the transaction.
    5. Mines a new blockchain block satisfying PoW difficulty ('00').
    6. Anchors block and transaction metadata into on-chain ledger tables.
    7. Updates encounter record with block_index and merkle_leaf_index for instant verification.
    """
    state = AppState.get_instance()
    patient = state.get_patient(req.patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient '{req.patient_id}' does not exist."
        )

    enc_id = f"enc-{uuid.uuid4()}"
    now_iso = datetime.now(timezone.utc).isoformat()

    with get_connection() as conn:
        # Check organization exists
        org_row = conn.execute("SELECT name FROM organizations WHERE id = ?", (req.organization_id,)).fetchone()
        miner_org_name = org_row["name"] if org_row else req.organization_id

        # Insert encounter base row
        provider_fk = req.provider_id if (req.provider_id and req.provider_id.strip()) else None
        payer_fk = req.payer_id if (req.payer_id and req.payer_id.strip()) else None

        conn.execute("""
            INSERT INTO encounters (
                id, patient_id, organization_id, provider_id, payer_id,
                encounter_class, code, description, start_time, stop_time, base_cost,
                total_claim_cost, payer_coverage
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            enc_id,
            req.patient_id,
            req.organization_id,
            provider_fk,
            payer_fk,
            req.encounter_class,
            req.code or "GENERAL_VISIT",
            req.description,
            now_iso,
            now_iso,
            req.base_cost,
            req.claim.total_claim_cost if req.claim else 0.0,
            req.claim.payer_coverage if req.claim else 0.0
        ))

        # Insert conditions
        for cond in req.conditions:
            conn.execute("""
                INSERT INTO conditions (encounter_id, patient_id, code, description, start_date)
                VALUES (?, ?, ?, ?, ?);
            """, (enc_id, req.patient_id, cond.code, cond.description, now_iso[:10]))

        # Insert medications
        for med in req.medications:
            conn.execute("""
                INSERT INTO medications (encounter_id, patient_id, code, description, start_date, dispenses, total_cost)
                VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (enc_id, req.patient_id, med.code, med.description, now_iso[:10], med.dispenses, med.total_cost))

        # Insert procedures
        for proc in req.procedures:
            conn.execute("""
                INSERT INTO procedures (encounter_id, patient_id, code, description, procedure_date, base_cost)
                VALUES (?, ?, ?, ?, ?, ?);
            """, (enc_id, req.patient_id, proc.code, proc.description, now_iso, proc.base_cost))

        # Insert immunizations
        for imm in req.immunizations:
            conn.execute("""
                INSERT INTO immunizations (encounter_id, patient_id, code, description, date)
                VALUES (?, ?, ?, ?, ?);
            """, (enc_id, req.patient_id, imm.code, imm.description, now_iso))

        # Insert observations
        for obs in req.observations:
            conn.execute("""
                INSERT INTO observations (encounter_id, patient_id, category, code, description, value, units, date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (enc_id, req.patient_id, obs.category, obs.code, obs.description, obs.value, obs.units, now_iso))

        # Insert claim (if provided)
        if req.claim:
            claim_id = f"clm-{uuid.uuid4()}"
            claim_payer_fk = req.claim.payer_id or payer_fk
            conn.execute("""
                INSERT INTO claims (
                    id, patient_id, encounter_id, provider_id, payer_id, service_date,
                    status, total_claim_cost, payer_coverage, diagnosis_code, procedure_code
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                claim_id,
                req.patient_id,
                enc_id,
                provider_fk,
                claim_payer_fk,
                now_iso,
                req.claim.status,
                req.claim.total_claim_cost,
                req.claim.payer_coverage,
                req.claim.diagnosis_code or "",
                req.claim.procedure_code or req.code or ""
            ))

    # Assemble canonical package and calculate SHA-256 fingerprint
    canonical_pkg = get_canonical_encounter_package(enc_id)
    if not canonical_pkg:
        raise HTTPException(status_code=500, detail="Failed to construct canonical package.")

    rec_hash = sha256_hash(canonical_json(canonical_pkg))
    canonical_pkg["record_hash"] = rec_hash

    # Dynamically anchor into a new block on the blockchain
    mining_result = state.anchor_new_encounter(canonical_pkg, miner_org=miner_org_name)

    log_audit(
        org_id=req.organization_id,
        action="CREATE_ENCOUNTER",
        patient_id=req.patient_id,
        record_id=enc_id,
        status="SUCCESS",
        details=f"Encounter created and anchored into Block #{mining_result['block_index']} (Hash: {rec_hash[:16]}...)"
    )

    return EncounterCreateResponse(**mining_result)


@router.get("/{encounter_id}/verify", response_model=VerificationResponse)
def verify_encounter_integrity(
    encounter_id: str,
    verifying_org: str = Query("VERIFIER", description="ID/Name of organization performing verification")
):
    """
    Performs full zero-trust cryptographic integrity verification on an encounter record.
    
    Verification Steps:
    1. Reconstructs the canonical EHR package from off-chain SQLite data.
    2. Calculates current_hash = SHA-256(canonical_json).
    3. Retrieves original anchored stored_hash from blockchain ledger.
    4. Compares current_hash == stored_hash (checks for off-chain tampering).
    5. Retrieves Merkle proof for the encounter's leaf index in the block.
    6. Validates Merkle proof up to block's merkle_root (O(log N)).
    7. Validates block header SHA-256, previous_hash linkage, and PoW nonce.
    8. Returns 'VERIFIED' or 'TAMPERED' with complete diagnostic audit trail.
    """
    with get_connection() as conn:
        enc_row = conn.execute("""
            SELECT id, patient_id, organization_id, record_hash, block_index, merkle_leaf_index
            FROM encounters WHERE id = ?;
        """, (encounter_id,)).fetchone()

        if not enc_row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Encounter '{encounter_id}' not found."
            )

        b_idx = enc_row["block_index"]
        leaf_idx = enc_row["merkle_leaf_index"]
        stored_hash = enc_row["record_hash"]

        # Fetch block header
        block_row = conn.execute("""
            SELECT block_index, timestamp, previous_hash, merkle_root, block_hash, nonce
            FROM blockchain_blocks WHERE block_index = ?;
        """, (b_idx,)).fetchone()

        if not block_row:
            raise HTTPException(status_code=500, detail=f"Blockchain block #{b_idx} missing from ledger.")

        # Fetch all transactions in this block to reconstruct Merkle tree and audit path
        tx_rows = conn.execute("""
            SELECT record_hash FROM blockchain_transactions
            WHERE block_index = ? ORDER BY leaf_index ASC;
        """, (b_idx,)).fetchall()
        leaves = [r["record_hash"] for r in tx_rows]

    # 1. Reconstruct canonical package from off-chain data
    current_pkg = get_canonical_encounter_package(encounter_id)
    if not current_pkg:
        raise HTTPException(status_code=500, detail="Failed to retrieve canonical package.")

    current_hash = sha256_hash(canonical_json(current_pkg))

    # 2. Check hash match
    hash_match = (current_hash == stored_hash)

    # 3. Generate and verify Merkle proof
    merkle_tree = MerkleTree(leaves)
    merkle_root = block_row["merkle_root"]
    
    proof = []
    merkle_proof_valid = False
    try:
        proof = merkle_tree.get_proof(leaf_idx)
        # Verify using current_hash to detect off-chain alterations
        merkle_proof_valid = MerkleTree.verify_proof(current_hash, proof, merkle_root)
    except Exception as e:
        merkle_proof_valid = False

    # 4. Check Blockchain block integrity
    header_str = f"{block_row['block_index']}:{block_row['timestamp']}:{block_row['previous_hash']}:{block_row['merkle_root']}:{block_row['nonce']}"
    recomputed_block_hash = sha256_hash(header_str)
    blockchain_valid = (recomputed_block_hash == block_row["block_hash"]) and block_row["block_hash"].startswith("00")

    # Final verdict
    is_fully_verified = hash_match and merkle_proof_valid and blockchain_valid
    integrity_status = "VERIFIED" if is_fully_verified else "TAMPERED"

    tamper_details = None
    if not hash_match:
        tamper_details = (
            f"Off-chain data was altered! Computed hash '{current_hash}' != stored anchored hash '{stored_hash}'."
        )
    elif not merkle_proof_valid:
        tamper_details = "Merkle proof verification failed against on-chain Merkle root."
    elif not blockchain_valid:
        tamper_details = "Blockchain block header or Proof-of-Work nonce is corrupted."

    # Record audit log event
    log_audit(
        org_id=verifying_org,
        action="VERIFY_INTEGRITY",
        patient_id=enc_row["patient_id"],
        record_id=encounter_id,
        status="SUCCESS" if is_fully_verified else "TAMPER_DETECTED",
        details=f"Verification result: {integrity_status}. {tamper_details or '100% Valid'}"
    )

    return VerificationResponse(
        encounter_id=encounter_id,
        patient_id=enc_row["patient_id"],
        organization_id=enc_row["organization_id"],
        current_hash=current_hash,
        stored_hash=stored_hash,
        hash_match=hash_match,
        block_index=b_idx,
        merkle_root=merkle_root,
        block_hash=block_row["block_hash"],
        merkle_proof=proof,
        merkle_proof_valid=merkle_proof_valid,
        blockchain_valid=blockchain_valid,
        integrity_status=integrity_status,
        tamper_details=tamper_details
    )
