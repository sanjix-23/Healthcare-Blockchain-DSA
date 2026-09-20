"""
Organization Authentication Endpoints.
NOTE: Patients DO NOT have login credentials or access to this system.
Only accredited healthcare organizations (Hospitals, Payers, Admins) authenticate.
"""

from fastapi import APIRouter, HTTPException, status
from core.crypto import sha256_hash
from db.database import get_connection, log_audit
from backend.models import LoginRequest, LoginResponse

router = APIRouter(prefix="/api/auth", tags=["Organization Authentication"])


@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest):
    """
    Authenticates an accredited organization (Hospital A, Hospital B, Insurance, Admin).
    Strictly denies patient login.
    """
    if "patient" in req.username.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Patient logins are not supported. This is an inter-organizational verification ledger."
        )

    pwd_hash = sha256_hash(req.password)
    with get_connection() as conn:
        user = conn.execute(
            "SELECT username, org_id, org_name, role FROM users WHERE username = ? AND password_hash = ?;",
            (req.username, pwd_hash)
        ).fetchone()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid organization credentials."
            )

        token = f"session_{user['role'].lower()}_{user['org_id'][:8]}"

        # Record audit trail
        log_audit(
            org_id=user["org_id"],
            action="LOGIN",
            status="SUCCESS",
            details=f"User '{user['username']}' logged in under role '{user['role']}'"
        )

        return LoginResponse(
            username=user["username"],
            org_id=user["org_id"],
            org_name=user["org_name"],
            role=user["role"],
            token=token
        )


@router.get("/demo-accounts")
def get_demo_accounts():
    """
    Returns pre-seeded demo accounts for quick role-switching in presentations.
    """
    return [
        {
            "role": "HOSPITAL",
            "org_name": "Hospital A (Lahey Hospital & Medical Center)",
            "username": "hospital_a",
            "password": "hospital_a_pass",
            "org_id": "6f122869-a856-3d65-8db9-099bf4f5bbb8",
            "description": "Primary care provider: creates initial records and anchors them on blockchain."
        },
        {
            "role": "HOSPITAL",
            "org_name": "Hospital B (Beth Israel Deaconess Hospital)",
            "username": "hospital_b",
            "password": "hospital_b_pass",
            "org_id": "b1ddf812-1fdd-3adf-b1d5-32cc8bd07ebb",
            "description": "Secondary provider: retrieves Hospital A records, verifies them, and adds new encounters."
        },
        {
            "role": "INSURANCE",
            "org_name": "Insurance (Blue Cross Blue Shield)",
            "username": "insurance_bcbs",
            "password": "insurance_pass",
            "org_id": "6e2f1a2d-27bd-3701-8d08-dae202c58632",
            "description": "Payer: verifies integrity of medical claims and prevents billing fraud."
        },
        {
            "role": "ADMIN",
            "org_name": "System Administrator",
            "username": "admin",
            "password": "admin_pass",
            "org_id": "SYS_ADMIN",
            "description": "Auditor: monitors full blockchain, tamper alerts, and performance metrics."
        }
    ]
