"""
In-Memory Service State for Healthcare Blockchain DSA Capstone.

Maintains:
1. In-memory CustomHashTable instances for O(1) patient ID and name lookups.
2. Blockchain instance loaded from SQLite for ledger operations and dynamic mining.
"""

import os
import sqlite3
from typing import Dict, List, Any, Optional
from core.hash_table import CustomHashTable
from core.blockchain import Blockchain, Block
from core.merkle_tree import MerkleTree
from db.database import get_connection, get_db_path


class AppState:
    """
    Singleton holding DSA in-memory structures and blockchain state.
    """
    _instance: Optional['AppState'] = None

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or get_db_path()
        # Custom Hash Tables for O(1) patient lookups
        self.patient_id_table = CustomHashTable(initial_capacity=2048)
        self.patient_name_table = CustomHashTable(initial_capacity=2048)
        self.blockchain = Blockchain(difficulty=2)
        self.is_initialized = False

    @classmethod
    def get_instance(cls, db_path: Optional[str] = None) -> 'AppState':
        if cls._instance is None:
            cls._instance = cls(db_path)
            cls._instance.initialize()
        return cls._instance

    def initialize(self) -> None:
        """
        Populates in-memory hash tables and reconstructs the blockchain ledger from SQLite.
        """
        if self.is_initialized:
            return

        with get_connection(self.db_path) as conn:
            # 1. Fetch organization visits per patient
            orgs_visited = {}
            cursor = conn.execute("""
                SELECT e.patient_id, o.name as org_name
                FROM encounters e
                JOIN organizations o ON e.organization_id = o.id
                GROUP BY e.patient_id, o.name;
            """)
            for row in cursor.fetchall():
                pid = row["patient_id"]
                if pid not in orgs_visited:
                    orgs_visited[pid] = []
                orgs_visited[pid].append(row["org_name"])

            # 2. Populate CustomHashTable with patient records
            cursor = conn.execute("""
                SELECT id, first_name, last_name, birthdate, gender, city, state, zip
                FROM patients;
            """)
            for row in cursor.fetchall():
                pid = row["id"]
                p_item = {
                    "id": pid,
                    "first_name": row["first_name"],
                    "last_name": row["last_name"],
                    "birthdate": str(row["birthdate"]),
                    "gender": row["gender"],
                    "city": row["city"],
                    "state": row["state"],
                    "zip": row["zip"],
                    "organizations_visited": orgs_visited.get(pid, [])
                }
                # Index by patient_id in CustomHashTable
                self.patient_id_table.put(pid, p_item)

                # Index by normalized name in CustomHashTable
                full_name = f"{row['first_name']} {row['last_name']}".strip().lower()
                existing_pids = self.patient_name_table.get(full_name) or []
                if pid not in existing_pids:
                    existing_pids.append(pid)
                self.patient_name_table.put(full_name, existing_pids)

            # 3. Load Blockchain ledger from database
            cursor = conn.execute("""
                SELECT block_index, timestamp, previous_hash, merkle_root, block_hash, nonce, miner_org
                FROM blockchain_blocks
                ORDER BY block_index ASC;
            """)
            block_rows = cursor.fetchall()
            
            reconstructed_blocks = []
            for b_row in block_rows:
                b_idx = b_row["block_index"]
                # Fetch transactions for this block
                tx_cursor = conn.execute("""
                    SELECT tx_id, record_id, patient_id, organization_id, record_hash, leaf_index, timestamp
                    FROM blockchain_transactions
                    WHERE block_index = ?
                    ORDER BY leaf_index ASC;
                """, (b_idx,))
                txs = [dict(tx) for tx in tx_cursor.fetchall()]

                block = Block(
                    index=b_idx,
                    timestamp=b_row["timestamp"],
                    previous_hash=b_row["previous_hash"],
                    merkle_root=b_row["merkle_root"],
                    transactions=txs,
                    nonce=b_row["nonce"],
                    miner_org=b_row["miner_org"],
                    block_hash=b_row["block_hash"]
                )
                reconstructed_blocks.append(block)

            self.blockchain.chain = reconstructed_blocks

        self.is_initialized = True

    def get_patient(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """
        O(1) average lookup using CustomHashTable.
        """
        return self.patient_id_table.get(patient_id)

    def search_patients(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Searches patients by ID or name using in-memory CustomHashTable and substring matching.
        """
        q = query.strip()
        if not q:
            # Return first `limit` items
            all_items = self.patient_id_table.values()
            return all_items[:limit]

        # 1. Exact ID lookup in O(1)
        exact_id = self.patient_id_table.get(q)
        if exact_id:
            return [exact_id]

        # 2. Exact Name lookup in O(1)
        q_lower = q.lower()
        matched_pids = self.patient_name_table.get(q_lower)
        if matched_pids:
            return [self.patient_id_table.get(pid) for pid in matched_pids if self.patient_id_table.get(pid)]

        # 3. Partial substring scan across cached items
        results = []
        for p in self.patient_id_table.values():
            if (q_lower in p["id"].lower() or
                q_lower in p["first_name"].lower() or
                q_lower in p["last_name"].lower() or
                q_lower in f"{p['first_name']} {p['last_name']}".lower()):
                results.append(p)
                if len(results) >= limit:
                    break

        return results

    def add_patient(self, p_dict: Dict[str, Any]) -> None:
        """
        Inserts newly registered patient into CustomHashTable.
        """
        pid = p_dict["id"]
        self.patient_id_table.put(pid, p_dict)
        full_name = f"{p_dict['first_name']} {p_dict['last_name']}".strip().lower()
        existing = self.patient_name_table.get(full_name) or []
        if pid not in existing:
            existing.append(pid)
        self.patient_name_table.put(full_name, existing)

    def anchor_new_encounter(self, enc_package: Dict[str, Any], miner_org: str) -> Dict[str, Any]:
        """
        Dynamically mines a new blockchain block for a newly added encounter
        and commits the transaction to both in-memory ledger and SQLite database.
        """
        eid = enc_package["record_id"]
        pid = enc_package["patient_id"]
        oid = enc_package["organization_id"]
        rec_hash = enc_package["record_hash"]

        with get_connection(self.db_path) as conn:
            # Latest block index
            latest = self.blockchain.get_latest_block()
            next_idx = latest.index + 1

            tx = {
                "tx_id": f"tx-{eid[:8]}-{next_idx}-0",
                "record_id": eid,
                "patient_id": pid,
                "organization_id": oid,
                "record_hash": rec_hash,
                "leaf_index": 0,
                "timestamp": enc_package["start_time"]
            }

            # Add and mine block via educational PoW
            mined_block = self.blockchain.add_block([tx], miner_org=miner_org)

            # Persist block to SQLite
            conn.execute("""
                INSERT INTO blockchain_blocks (block_index, timestamp, previous_hash, merkle_root, block_hash, nonce, tx_count, miner_org)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                mined_block.index,
                mined_block.timestamp,
                mined_block.previous_hash,
                mined_block.merkle_root,
                mined_block.block_hash,
                mined_block.nonce,
                1,
                mined_block.miner_org
            ))

            # Persist transaction to SQLite
            conn.execute("""
                INSERT INTO blockchain_transactions (tx_id, block_index, record_id, patient_id, organization_id, record_hash, leaf_index, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                tx["tx_id"],
                mined_block.index,
                tx["record_id"],
                tx["patient_id"],
                tx["organization_id"],
                tx["record_hash"],
                tx["leaf_index"],
                tx["timestamp"]
            ))

            # Update encounter record with block index and leaf index
            conn.execute("""
                UPDATE encounters
                SET block_index = ?, merkle_leaf_index = ?, record_hash = ?
                WHERE id = ?;
            """, (mined_block.index, 0, rec_hash, eid))

            # Update patient's organizations_visited in in-memory index
            org_row = conn.execute("SELECT name FROM organizations WHERE id = ?", (oid,)).fetchone()
            org_name = org_row["name"] if org_row else oid
            
            p_summary = self.patient_id_table.get(pid)
            if p_summary:
                if org_name not in p_summary["organizations_visited"]:
                    p_summary["organizations_visited"].append(org_name)
                    self.patient_id_table.put(pid, p_summary)

        return {
            "encounter_id": eid,
            "patient_id": pid,
            "record_hash": rec_hash,
            "block_index": mined_block.index,
            "merkle_leaf_index": 0,
            "merkle_root": mined_block.merkle_root,
            "block_hash": mined_block.block_hash,
            "status": "ANCHORED"
        }
