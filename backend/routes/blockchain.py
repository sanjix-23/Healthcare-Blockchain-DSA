"""
Blockchain Explorer and Chain Validation Endpoints.
Provides transparent inspection of the educational hash-linked ledger.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from db.database import get_connection, log_audit
from backend.state import AppState

router = APIRouter(prefix="/api/blockchain", tags=["Blockchain Ledger Explorer"])


@router.get("/summary")
def get_blockchain_summary():
    """
    Returns high-level statistics about the blockchain ledger.
    """
    state = AppState.get_instance()
    chain = state.blockchain.chain

    with get_connection() as conn:
        tx_count = conn.execute("SELECT COUNT(*) FROM blockchain_transactions;").fetchone()[0]

    latest = state.blockchain.get_latest_block()
    return {
        "total_blocks": len(chain),
        "total_transactions": tx_count,
        "difficulty_target": f"{state.blockchain.difficulty} leading zeros ('00')",
        "latest_block_index": latest.index,
        "latest_block_hash": latest.block_hash,
        "latest_merkle_root": latest.merkle_root,
        "ledger_type": "Local Educational Hash-Linked Blockchain Prototype (SQLite Persistence)"
    }


@router.get("/blocks")
def list_blocks(
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0)
):
    """
    Lists block headers with pagination for the blockchain explorer.
    """
    with get_connection() as conn:
        total = conn.execute("SELECT COUNT(*) FROM blockchain_blocks;").fetchone()[0]
        rows = conn.execute("""
            SELECT block_index, timestamp, previous_hash, merkle_root, block_hash, nonce, tx_count, miner_org
            FROM blockchain_blocks
            ORDER BY block_index ASC
            LIMIT ? OFFSET ?;
        """, (limit, offset)).fetchall()

    return {
        "total_blocks": total,
        "limit": limit,
        "offset": offset,
        "blocks": [dict(r) for r in rows]
    }


@router.get("/blocks/{block_index}")
def get_block_details(block_index: int):
    """
    Returns full block details including all contained transactions and Merkle root.
    """
    with get_connection() as conn:
        b_row = conn.execute("""
            SELECT * FROM blockchain_blocks WHERE block_index = ?;
        """, (block_index,)).fetchone()

        if not b_row:
            raise HTTPException(status_code=404, detail=f"Block #{block_index} not found.")

        tx_rows = conn.execute("""
            SELECT bt.*, e.description as encounter_desc, e.patient_id, o.name as org_name
            FROM blockchain_transactions bt
            LEFT JOIN encounters e ON bt.record_id = e.id
            LEFT JOIN organizations o ON bt.organization_id = o.id
            WHERE bt.block_index = ?
            ORDER BY bt.leaf_index ASC;
        """, (block_index,)).fetchall()

    block_data = dict(b_row)
    block_data["transactions"] = [dict(tx) for tx in tx_rows]
    return block_data


@router.get("/validate")
def validate_entire_blockchain():
    """
    Performs complete cryptographic verification over all blocks in the blockchain:
    - Recomputes SHA-256 header hash of each block.
    - Validates previous_hash linkage between consecutive blocks.
    - Validates Proof-of-Work nonce meeting difficulty ('00').
    - Reconstructs binary Merkle tree from transactions to confirm merkle_root.
    """
    state = AppState.get_instance()
    is_valid, message = state.blockchain.is_valid_chain()

    log_audit(
        org_id="ADMIN_EXPLORER",
        action="BLOCKCHAIN_AUDIT",
        status="SUCCESS" if is_valid else "CORRUPTED",
        details=f"Blockchain validation result: {message}"
    )

    return {
        "is_valid": is_valid,
        "total_blocks_verified": len(state.blockchain.chain),
        "status": "VALID" if is_valid else "CORRUPTED",
        "message": message
    }
