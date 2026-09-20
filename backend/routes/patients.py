"""
Patient Search and Longitudinal EHR Endpoints.
Enforces strict security & data minimization.
Utilizes custom CustomHashTable and PatientHistoryLinkedList data structures.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from core.linked_list import PatientHistoryLinkedList, HistoryNode
from db.database import get_connection, log_audit
from backend.state import AppState
from backend.models import (
    PatientSearchItem,
    PatientCreateRequest,
    PatientCreateResponse
)

router = APIRouter(prefix="/api/patients", tags=["Patient & EHR Management"])


@router.get("/search", response_model=List[PatientSearchItem])
def search_patients(
    q: str = Query("", description="Search by Patient ID or Name"),
    limit: int = Query(50, ge=1, le=200)
):
    """
    Searches patient registry using the in-memory CustomHashTable with bucket chaining.
    Returns non-sensitive demographic summaries and lists organizations visited.
    Does NOT expose SSN, passport, driver's license, lat/lon, or street addresses.
    """
    state = AppState.get_instance()
    results = state.search_patients(q, limit)

    log_audit(
        org_id="QUERY_SERVICE",
        action="SEARCH_PATIENT",
        status="SUCCESS",
        details=f"Search query: '{q}', returned {len(results)} matches"
    )

    return [PatientSearchItem(**p) for p in results]


@router.get("/{patient_id}")
def get_patient_details(patient_id: str):
    """
    Retrieves individual patient demographic profile via O(1) CustomHashTable lookup.
    """
    state = AppState.get_instance()
    patient = state.get_patient(patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient '{patient_id}' not found."
        )
    return patient


@router.get("/{patient_id}/ehr")
def get_patient_ehr(patient_id: str, requesting_org: str = "HOSPITAL_USER"):
    """
    Retrieves the unified longitudinal EHR for a patient across all visiting hospitals.
    Assembles the clinical encounters into a chronological PatientHistoryLinkedList (DSA).
    
    Structure:
    Patient Profile
      └── Encounters (Linked List)
            ├── Originating Hospital & Provider
            ├── Conditions (Diagnoses)
            ├── Medications (Prescriptions)
            ├── Procedures
            ├── Observations (Vitals & Labs)
            ├── Immunizations
            └── Claim / Billing Information
    """
    state = AppState.get_instance()
    patient = state.get_patient(patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient '{patient_id}' not found."
        )

    history_list = PatientHistoryLinkedList()

    with get_connection() as conn:
        # Fetch all encounters for this patient ordered by start_time
        enc_rows = conn.execute("""
            SELECT e.*, o.name as org_name, p.name as provider_name
            FROM encounters e
            LEFT JOIN organizations o ON e.organization_id = o.id
            LEFT JOIN providers p ON e.provider_id = p.id
            WHERE e.patient_id = ?
            ORDER BY e.start_time ASC;
        """, (patient_id,)).fetchall()

        for enc in enc_rows:
            eid = enc["id"]

            # Fetch conditions
            conds = [dict(r) for r in conn.execute(
                "SELECT code, description FROM conditions WHERE encounter_id = ? ORDER BY code", (eid,)
            ).fetchall()]

            # Fetch medications
            meds = [dict(r) for r in conn.execute(
                "SELECT code, description, dispenses, total_cost FROM medications WHERE encounter_id = ? ORDER BY code", (eid,)
            ).fetchall()]

            # Fetch procedures
            procs = [dict(r) for r in conn.execute(
                "SELECT code, description, base_cost FROM procedures WHERE encounter_id = ? ORDER BY code", (eid,)
            ).fetchall()]

            # Fetch immunizations
            imms = [dict(r) for r in conn.execute(
                "SELECT code, description FROM immunizations WHERE encounter_id = ? ORDER BY code", (eid,)
            ).fetchall()]

            # Fetch observations
            obs = [dict(r) for r in conn.execute(
                "SELECT category, code, description, value, units FROM observations WHERE encounter_id = ? ORDER BY code", (eid,)
            ).fetchall()]

            # Fetch claim
            claims = [dict(r) for r in conn.execute(
                "SELECT id, payer_id, status, total_claim_cost, payer_coverage, diagnosis_code, procedure_code "
                "FROM claims WHERE encounter_id = ?", (eid,)
            ).fetchall()]

            # Instantiate custom HistoryNode (Singly Linked List node)
            node = HistoryNode(
                encounter_id=eid,
                patient_id=patient_id,
                organization_id=enc["organization_id"],
                provider_id=enc["provider_id"] or "",
                start_time=enc["start_time"],
                stop_time=enc["stop_time"] or enc["start_time"],
                encounter_class=enc["encounter_class"],
                description=enc["description"],
                base_cost=float(enc["base_cost"]),
                record_hash=enc["record_hash"] or "",
                block_index=enc["block_index"],
                merkle_leaf_index=enc["merkle_leaf_index"],
                conditions=conds,
                medications=meds,
                procedures=procs,
                immunizations=imms,
                observations=obs,
                claims=claims
            )
            # Append to custom PatientHistoryLinkedList in O(1)
            history_list.append(node)

    log_audit(
        org_id=requesting_org,
        action="VIEW_EHR",
        patient_id=patient_id,
        status="SUCCESS",
        details=f"Retrieved {len(history_list)} encounters from longitudinal linked list"
    )

    return {
        "patient": patient,
        "encounter_count": len(history_list),
        "encounters": history_list.to_list()
    }


@router.post("", response_model=PatientCreateResponse, status_code=status.HTTP_201_CREATED)
def register_new_patient(req: PatientCreateRequest, registering_org: str = "HOSPITAL_A"):
    """
    Registers a new patient sequentially after the 1,163 Synthea patients.
    Automatically assigns the next sequential identifier (e.g. P001164, P001165).
    Inserts into SQLite and in-memory CustomHashTable.
    """
    with get_connection() as conn:
        # Find next sequential ID
        cursor = conn.execute("SELECT id FROM patients WHERE id LIKE 'P%' ORDER BY id DESC LIMIT 1;")
        last_p = cursor.fetchone()

        if last_p and last_p["id"].startswith("P") and last_p["id"][1:].isdigit():
            next_num = int(last_p["id"][1:]) + 1
            new_id = f"P{next_num:06d}"
        else:
            total_count = conn.execute("SELECT COUNT(*) FROM patients;").fetchone()[0]
            new_id = f"P{total_count + 1:06d}"

        # Insert into SQLite
        conn.execute("""
            INSERT INTO patients (id, first_name, last_name, birthdate, gender, race, ethnicity, city, state, zip)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            new_id,
            req.first_name,
            req.last_name,
            req.birthdate,
            req.gender,
            req.race or "white",
            req.ethnicity or "nonhispanic",
            req.city,
            req.state,
            req.zip
        ))

    # Add to in-memory CustomHashTable
    p_summary = {
        "id": new_id,
        "first_name": req.first_name,
        "last_name": req.last_name,
        "birthdate": req.birthdate,
        "gender": req.gender,
        "city": req.city,
        "state": req.state,
        "zip": req.zip,
        "organizations_visited": []
    }
    AppState.get_instance().add_patient(p_summary)

    log_audit(
        org_id=registering_org,
        action="CREATE_PATIENT",
        patient_id=new_id,
        status="SUCCESS",
        details=f"Dynamically registered new patient {req.first_name} {req.last_name} ({new_id})"
    )

    return PatientCreateResponse(
        patient_id=new_id,
        first_name=req.first_name,
        last_name=req.last_name,
        message=f"Patient {new_id} successfully created and indexed."
    )
