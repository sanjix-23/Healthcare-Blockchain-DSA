"""
Database Access Layer for Healthcare Blockchain DSA Capstone.

Handles SQLite connection management, schema initialization, and transactional
CRUD queries for both off-chain clinical tables and on-chain ledger tables.
"""

import os
import sqlite3
from contextlib import contextmanager
from typing import Generator, List, Dict, Any, Optional
from core.crypto import sha256_hash

DEFAULT_DB_PATH = os.path.join(r"C:\Healthcare-Blockchain-DSA\blockchain_data", "healthcare_ehr.db")
SCHEMA_PATH = os.path.join(r"C:\Healthcare-Blockchain-DSA\db", "schema.sql")


def get_db_path() -> str:
    """
    Returns the absolute path to the SQLite database file.
    Ensures the parent directory exists.
    """
    os.makedirs(os.path.dirname(DEFAULT_DB_PATH), exist_ok=True)
    return DEFAULT_DB_PATH


@contextmanager
def get_connection(db_path: Optional[str] = None) -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager providing an SQLite connection with row_factory enabled.
    """
    path = db_path or get_db_path()
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(db_path: Optional[str] = None) -> None:
    """
    Initializes database tables using db/schema.sql and seeds default organization users.
    """
    path = db_path or get_db_path()
    with get_connection(path) as conn:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        
        # Seed default organization users if not present
        seed_default_users(conn)


def seed_default_users(conn: sqlite3.Connection) -> None:
    """
    Seeds organization credentials for demo presentation.
    NO PATIENT USERS ARE CREATED.
    """
    default_users = [
        ("hospital_a", sha256_hash("hospital_a_pass"), "6f122869-a856-3d65-8db9-099bf4f5bbb8", "LAHEY HOSPITAL & MEDICAL CENTER", "HOSPITAL"),
        ("hospital_b", sha256_hash("hospital_b_pass"), "b1ddf812-1fdd-3adf-b1d5-32cc8bd07ebb", "BETH ISRAEL DEACONESS HOSPITAL", "HOSPITAL"),
        ("insurance_bcbs", sha256_hash("insurance_pass"), "6e2f1a2d-27bd-3701-8d08-dae202c58632", "BLUE CROSS BLUE SHIELD", "INSURANCE"),
        ("insurance_medicare", sha256_hash("medicare_pass"), "7caa7254-5050-3b5e-9eae-bd5ea30e809c", "MEDICARE", "INSURANCE"),
        ("admin", sha256_hash("admin_pass"), "SYS_ADMIN", "SYSTEM ADMINISTRATOR", "ADMIN")
    ]
    for username, pwd_hash, org_id, org_name, role in default_users:
        conn.execute("""
            INSERT OR IGNORE INTO users (username, password_hash, org_id, org_name, role)
            VALUES (?, ?, ?, ?, ?);
        """, (username, pwd_hash, org_id, org_name, role))


def get_canonical_encounter_package(encounter_id: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Constructs the canonical clinical package for an encounter to compute or verify its SHA-256 fingerprint.
    Includes:
    - Base encounter data
    - Conditions (diagnoses)
    - Medications (prescriptions)
    - Procedures
    - Immunizations
    - Observations (vitals/labs)
    - Claims (billing information including procedure_code and costs)
    
    Any modification to ANY of these fields alters the canonical JSON and causes verification to fail.
    """
    path = db_path or get_db_path()
    with get_connection(path) as conn:
        enc_row = conn.execute("SELECT * FROM encounters WHERE id = ?", (encounter_id,)).fetchone()
        if not enc_row:
            return None

        # Fetch conditions
        cond_rows = conn.execute(
            "SELECT code, description FROM conditions WHERE encounter_id = ? ORDER BY code, description",
            (encounter_id,)
        ).fetchall()
        conditions = [{"code": r["code"], "description": r["description"]} for r in cond_rows]

        # Fetch medications
        med_rows = conn.execute(
            "SELECT code, description, dispenses, total_cost FROM medications WHERE encounter_id = ? ORDER BY code",
            (encounter_id,)
        ).fetchall()
        medications = [{
            "code": r["code"],
            "description": r["description"],
            "dispenses": r["dispenses"],
            "total_cost": float(r["total_cost"])
        } for r in med_rows]

        # Fetch procedures
        proc_rows = conn.execute(
            "SELECT code, description, base_cost FROM procedures WHERE encounter_id = ? ORDER BY code",
            (encounter_id,)
        ).fetchall()
        procedures = [{
            "code": r["code"],
            "description": r["description"],
            "base_cost": float(r["base_cost"])
        } for r in proc_rows]

        # Fetch immunizations
        imm_rows = conn.execute(
            "SELECT code, description FROM immunizations WHERE encounter_id = ? ORDER BY code",
            (encounter_id,)
        ).fetchall()
        immunizations = [{"code": r["code"], "description": r["description"]} for r in imm_rows]

        # Fetch observations
        obs_rows = conn.execute(
            "SELECT category, code, description, value, units FROM observations WHERE encounter_id = ? ORDER BY code",
            (encounter_id,)
        ).fetchall()
        observations = [{
            "category": r["category"],
            "code": r["code"],
            "description": r["description"],
            "value": r["value"],
            "units": r["units"]
        } for r in obs_rows]

        # Fetch associated claim (Billing fields bound into canonical package)
        claim_row = conn.execute(
            "SELECT id, payer_id, status, total_claim_cost, payer_coverage, diagnosis_code, procedure_code "
            "FROM claims WHERE encounter_id = ?",
            (encounter_id,)
        ).fetchone()

        claim_info = None
        if claim_row:
            claim_info = {
                "claim_id": claim_row["id"],
                "payer_id": claim_row["payer_id"],
                "status": claim_row["status"],
                "total_claim_cost": float(claim_row["total_claim_cost"]),
                "payer_coverage": float(claim_row["payer_coverage"]),
                "diagnosis_code": claim_row["diagnosis_code"] or "",
                "procedure_code": claim_row["procedure_code"] or ""
            }

        package = {
            "record_id": enc_row["id"],
            "patient_id": enc_row["patient_id"],
            "organization_id": enc_row["organization_id"],
            "provider_id": enc_row["provider_id"],
            "payer_id": enc_row["payer_id"],
            "encounter_class": enc_row["encounter_class"],
            "code": enc_row["code"],
            "description": enc_row["description"],
            "start_time": enc_row["start_time"],
            "stop_time": enc_row["stop_time"],
            "base_cost": float(enc_row["base_cost"]),
            "conditions": conditions,
            "medications": medications,
            "procedures": procedures,
            "immunizations": immunizations,
            "observations": observations,
            "claim": claim_info
        }
        return package


def log_audit(
    org_id: str,
    action: str,
    patient_id: Optional[str] = None,
    record_id: Optional[str] = None,
    status: str = "SUCCESS",
    details: str = "",
    db_path: Optional[str] = None
) -> None:
    """
    Inserts an immutable audit trail event.
    """
    path = db_path or get_db_path()
    with get_connection(path) as conn:
        conn.execute("""
            INSERT INTO audit_log (org_id, action, patient_id, record_id, status, details)
            VALUES (?, ?, ?, ?, ?, ?);
        """, (org_id, action, patient_id, record_id, status, details))
