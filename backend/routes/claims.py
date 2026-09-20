"""
Insurance Claim Search and Billing Integrity Verification Endpoints.
Allows health insurance companies (Payers) to inspect claims and cryptographically
verify that billing codes and costs have not been altered after hospital discharge.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from db.database import get_connection, log_audit
from backend.routes.encounters import verify_encounter_integrity

router = APIRouter(prefix="/api/claims", tags=["Insurance Claims & Billing Integrity"])


@router.get("/search")
def search_claims(
    patient_id: Optional[str] = Query(None, description="Filter by Patient ID"),
    claim_id: Optional[str] = Query(None, description="Filter by Claim ID"),
    payer_id: Optional[str] = Query(None, description="Filter by Payer ID"),
    limit: int = Query(50, ge=1, le=200)
):
    """
    Searches billing claims with associated encounter IDs and hospital provider details.
    """
    query = """
        SELECT c.*, p.first_name, p.last_name, e.description as encounter_desc,
               e.organization_id, o.name as org_name
        FROM claims c
        JOIN patients p ON c.patient_id = p.id
        JOIN encounters e ON c.encounter_id = e.id
        LEFT JOIN organizations o ON e.organization_id = o.id
        WHERE 1=1
    """
    params = []
    if patient_id:
        query += " AND c.patient_id = ?"
        params.append(patient_id)
    if claim_id:
        query += " AND c.id = ?"
        params.append(claim_id)
    if payer_id:
        query += " AND c.payer_id = ?"
        params.append(payer_id)

    query += " ORDER BY c.service_date DESC LIMIT ?;"
    params.append(limit)

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()

    return [dict(r) for r in rows]


@router.get("/{claim_id}")
def get_claim_details(claim_id: str):
    """
    Retrieves complete claim billing records alongside associated encounter clinical data.
    """
    with get_connection() as conn:
        claim_row = conn.execute("""
            SELECT c.*, p.first_name, p.last_name, e.description as encounter_desc,
                   e.record_hash, e.block_index, o.name as hospital_name
            FROM claims c
            JOIN patients p ON c.patient_id = p.id
            JOIN encounters e ON c.encounter_id = e.id
            LEFT JOIN organizations o ON e.organization_id = o.id
            WHERE c.id = ?;
        """, (claim_id,)).fetchone()

        if not claim_row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Claim '{claim_id}' not found."
            )

    return dict(claim_row)


@router.get("/{claim_id}/verify")
def verify_claim_integrity(
    claim_id: str,
    verifying_payer: str = Query("INSURANCE_USER", description="Payer verifying the claim")
):
    """
    Verifies that the claim's billing fields (procedure_code, diagnosis_code, total_claim_cost, payer_coverage)
    match the immutable cryptographic hash anchored in the blockchain by the hospital.
    """
    with get_connection() as conn:
        claim_row = conn.execute("SELECT id, encounter_id, patient_id FROM claims WHERE id = ?;", (claim_id,)).fetchone()
        if not claim_row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Claim '{claim_id}' not found."
            )
        enc_id = claim_row["encounter_id"]

    # Execute cryptographic verification on the associated encounter package
    verif_result = verify_encounter_integrity(encounter_id=enc_id, verifying_org=verifying_payer)

    log_audit(
        org_id=verifying_payer,
        action="VERIFY_CLAIM",
        patient_id=claim_row["patient_id"],
        record_id=claim_id,
        status="SUCCESS" if verif_result.integrity_status == "VERIFIED" else "TAMPER_DETECTED",
        details=f"Claim verification for '{claim_id}' completed with status: {verif_result.integrity_status}"
    )

    return {
        "claim_id": claim_id,
        "encounter_id": enc_id,
        "patient_id": claim_row["patient_id"],
        "billing_integrity_verified": (verif_result.integrity_status == "VERIFIED"),
        "verification_details": verif_result
    }
