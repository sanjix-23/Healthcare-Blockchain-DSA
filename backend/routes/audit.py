"""
Audit Trail Endpoints.
Utilizes the custom AuditLogLinkedList data structure to traverse immutable system events.
"""

from typing import Optional
from fastapi import APIRouter, Query
from core.linked_list import AuditLogLinkedList, AuditNode
from db.database import get_connection

router = APIRouter(prefix="/api/audit", tags=["Audit Trail"])


@router.get("")
def get_audit_trail(
    limit: int = Query(50, ge=1, le=200),
    org_id: Optional[str] = Query(None, description="Filter by organization"),
    action: Optional[str] = Query(None, description="Filter by action type")
):
    """
    Returns system audit trail using custom AuditLogLinkedList (DSA).
    Logs logins, patient searches, EHR views, integrity verifications, and tamper tests.
    """
    query = "SELECT * FROM audit_log WHERE 1=1"
    params = []
    if org_id:
        query += " AND org_id = ?"
        params.append(org_id)
    if action:
        query += " AND action = ?"
        params.append(action)

    query += " ORDER BY id DESC LIMIT ?;"
    params.append(limit)

    audit_list = AuditLogLinkedList()
    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
        for r in rows:
            node = AuditNode(
                event_id=r["id"],
                timestamp=str(r["timestamp"]),
                org_id=r["org_id"],
                action=r["action"],
                patient_id=r["patient_id"],
                record_id=r["record_id"],
                status=r["status"],
                details=r["details"] or ""
            )
            audit_list.append(node)

    return {
        "event_count": len(audit_list),
        "events": audit_list.to_list()
    }
