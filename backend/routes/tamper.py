"""
Tamper Simulation Endpoints for Educational Capstone Demonstration.
Allows modifying off-chain SQLite fields WITHOUT modifying the blockchain ledger,
demonstrating how SHA-256 and Merkle proof verification detect unauthorized edits.
Includes 1-click restore functionality for seamless presentation repeats.
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status
from db.database import get_connection, log_audit
from backend.models import (
    TamperClinicalRequest,
    TamperBillingRequest,
    TamperRestoreRequest
)

router = APIRouter(prefix="/api/tamper", tags=["Tamper Simulation (Demo Only)"])

# In-memory backup cache to allow 1-click restoration during presentations
_tamper_backups: Dict[str, Dict[str, Any]] = {}


@router.post("/clinical")
def simulate_clinical_tamper(req: TamperClinicalRequest):
    """
    Simulates malicious off-chain clinical alteration:
    Modifies a condition or encounter description in SQLite without touching the blockchain ledger.
    """
    with get_connection() as conn:
        enc = conn.execute("SELECT id, description, record_hash FROM encounters WHERE id = ?;", (req.encounter_id,)).fetchone()
        if not enc:
            raise HTTPException(status_code=404, detail=f"Encounter '{req.encounter_id}' not found.")

        # Check if conditions exist for this encounter
        cond = conn.execute("SELECT id, description FROM conditions WHERE encounter_id = ? LIMIT 1;", (req.encounter_id,)).fetchone()

        # Save backup
        if req.encounter_id not in _tamper_backups:
            _tamper_backups[req.encounter_id] = {}

        if cond:
            _tamper_backups[req.encounter_id]["cond_id"] = cond["id"]
            _tamper_backups[req.encounter_id]["orig_condition"] = cond["description"]
            conn.execute(
                "UPDATE conditions SET description = ? WHERE id = ?;",
                (req.new_value, cond["id"])
            )
            tampered_entity = f"Condition #{cond['id']} modified to: '{req.new_value}'"
        else:
            _tamper_backups[req.encounter_id]["orig_desc"] = enc["description"]
            conn.execute(
                "UPDATE encounters SET description = ? WHERE id = ?;",
                (req.new_value, req.encounter_id)
            )
            tampered_entity = f"Encounter description modified to: '{req.new_value}'"

    log_audit(
        org_id="SIMULATOR",
        action="TAMPER_SIMULATION",
        record_id=req.encounter_id,
        status="TAMPER_APPLIED",
        details=f"Educational clinical tampering applied: {tampered_entity}"
    )

    return {
        "encounter_id": req.encounter_id,
        "tamper_type": "CLINICAL",
        "action": "Off-chain database modified successfully.",
        "details": tampered_entity,
        "next_step": "Run GET /api/encounters/{id}/verify to see the RED TAMPER ALERT."
    }


@router.post("/billing")
def simulate_billing_tamper(req: TamperBillingRequest):
    """
    Simulates healthcare billing fraud / upcoding:
    Modifies total_claim_cost or procedure_code in the claims table.
    """
    with get_connection() as conn:
        claim = conn.execute("SELECT id, total_claim_cost, procedure_code FROM claims WHERE encounter_id = ? LIMIT 1;", (req.encounter_id,)).fetchone()
        if not claim:
            raise HTTPException(status_code=404, detail=f"No billing claim found for encounter '{req.encounter_id}'.")

        # Save backup
        if req.encounter_id not in _tamper_backups:
            _tamper_backups[req.encounter_id] = {}

        _tamper_backups[req.encounter_id]["claim_id"] = claim["id"]
        _tamper_backups[req.encounter_id]["orig_cost"] = claim["total_claim_cost"]
        _tamper_backups[req.encounter_id]["orig_proc"] = claim["procedure_code"]

        if req.field == "procedure_code":
            conn.execute("UPDATE claims SET procedure_code = ? WHERE id = ?;", (str(req.new_value), claim["id"]))
            tampered_detail = f"Procedure code inflated to '{req.new_value}'"
        else:
            cost_val = float(req.new_value)
            conn.execute("UPDATE claims SET total_claim_cost = ? WHERE id = ?;", (cost_val, claim["id"]))
            tampered_detail = f"Claim billing cost inflated from ${claim['total_claim_cost']} to ${cost_val}"

    log_audit(
        org_id="SIMULATOR",
        action="TAMPER_SIMULATION",
        record_id=req.encounter_id,
        status="TAMPER_APPLIED",
        details=f"Educational billing tampering applied: {tampered_detail}"
    )

    return {
        "encounter_id": req.encounter_id,
        "tamper_type": "BILLING_CLAIM",
        "action": "Off-chain billing claim modified successfully.",
        "details": tampered_detail,
        "next_step": "Run GET /api/claims/{claim_id}/verify or encounter verify to detect billing fraud."
    }


@router.post("/restore")
def restore_tampered_record(req: TamperRestoreRequest):
    """
    Restores the original off-chain clinical and billing data from backup.
    Allows repeated viva demonstrations without database corruption.
    """
    backup = _tamper_backups.get(req.encounter_id)
    if not backup:
        raise HTTPException(
            status_code=400,
            detail=f"No active tamper backup recorded for encounter '{req.encounter_id}'."
        )

    with get_connection() as conn:
        if "cond_id" in backup:
            conn.execute(
                "UPDATE conditions SET description = ? WHERE id = ?;",
                (backup["orig_condition"], backup["cond_id"])
            )
        if "orig_desc" in backup:
            conn.execute(
                "UPDATE encounters SET description = ? WHERE id = ?;",
                (backup["orig_desc"], req.encounter_id)
            )
        if "claim_id" in backup:
            conn.execute(
                "UPDATE claims SET total_claim_cost = ?, procedure_code = ? WHERE id = ?;",
                (backup["orig_cost"], backup["orig_proc"], backup["claim_id"])
            )

    del _tamper_backups[req.encounter_id]

    log_audit(
        org_id="SIMULATOR",
        action="TAMPER_RESTORE",
        record_id=req.encounter_id,
        status="SUCCESS",
        details="Original off-chain data restored successfully."
    )

    return {
        "encounter_id": req.encounter_id,
        "status": "RESTORED",
        "message": "Original off-chain clinical and billing data restored. Record is now VERIFIED again."
    }
