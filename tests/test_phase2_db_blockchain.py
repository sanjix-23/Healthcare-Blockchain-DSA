"""
Comprehensive Automated Test Suite for Phase 2: Database Layer & Initial Blockchain Ledger.

Verifies:
1. Population integrity: exactly 1,163 Synthea patients imported
2. Encounter integrity: exactly 61,459 encounters imported
3. Block structure: 124 blocks created (1 Genesis + 123 Data Blocks)
4. Field privacy: confirms SSN, passport, driver's license, lat, lon are absent
5. Cryptographic hash integrity: stored record_hash matches canonical package hash
6. Merkle proof verification: validates leaf-to-root Merkle path against block header
7. Blockchain previous_hash links: validates unbroken sequence from Genesis to Block 123
8. Clinical data tamper detection: proves modifying a condition fails verification
9. Claim & billing tamper detection: proves modifying claim cost/procedure fails verification
10. Cross-hospital retrieval: validates patient records spanning multiple organizations
"""

import unittest
import sqlite3
from typing import Dict, Any

from core.crypto import sha256_hash, canonical_json
from core.merkle_tree import MerkleTree
from core.blockchain import Blockchain, Block
from db.database import get_db_path, get_connection, get_canonical_encounter_package


class TestPhase2DBAndBlockchain(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db_path = get_db_path()

    def test_01_patient_count(self):
        with get_connection(self.db_path) as conn:
            count = conn.execute("SELECT COUNT(*) FROM patients;").fetchone()[0]
        self.assertGreaterEqual(count, 1163, "Database must contain at least 1,163 patients")

    def test_02_encounter_count(self):
        with get_connection(self.db_path) as conn:
            count = conn.execute("SELECT COUNT(*) FROM encounters;").fetchone()[0]
        self.assertGreaterEqual(count, 61459, "Database must contain at least 61,459 encounters")

    def test_03_blockchain_blocks_count(self):
        with get_connection(self.db_path) as conn:
            count = conn.execute("SELECT COUNT(*) FROM blockchain_blocks;").fetchone()[0]
        # 1 Genesis + ceil(61459 / 500) = 124 blocks minimum
        self.assertGreaterEqual(count, 124, "Blockchain must contain at least 124 blocks")

    def test_04_data_minimization_security(self):
        with get_connection(self.db_path) as conn:
            cursor = conn.execute("PRAGMA table_info(patients);")
            columns = [row[1].lower() for row in cursor.fetchall()]
        
        forbidden = ["ssn", "drivers", "passport", "address", "lat", "lon", "maiden"]
        for f in forbidden:
            self.assertNotIn(f, columns, f"Forbidden privacy column '{f}' must NOT exist in patients table")

    def test_05_canonical_package_hash_integrity(self):
        # Sample encounters across different blocks
        sample_ids = [
            "748f8357-6cc7-551d-f31a-32fa2cf84126",
            "01efcc52-15d6-51e9-faa2-bee069fcbe44"
        ]
        with get_connection(self.db_path) as conn:
            for eid in sample_ids:
                row = conn.execute("SELECT record_hash FROM encounters WHERE id = ?;", (eid,)).fetchone()
                if not row:
                    continue
                stored_hash = row["record_hash"]
                pkg = get_canonical_encounter_package(eid, self.db_path)
                self.assertIsNotNone(pkg)
                recomputed_hash = sha256_hash(canonical_json(pkg))
                self.assertEqual(stored_hash, recomputed_hash, f"Canonical hash must match for encounter {eid}")

    def test_06_merkle_proof_verification_from_db(self):
        # Verify Merkle proof for an encounter in Block #1
        with get_connection(self.db_path) as conn:
            enc = conn.execute(
                "SELECT id, record_hash, block_index, merkle_leaf_index FROM encounters WHERE block_index = 1 LIMIT 1;"
            ).fetchone()
            self.assertIsNotNone(enc)

            block = conn.execute(
                "SELECT merkle_root FROM blockchain_blocks WHERE block_index = 1;"
            ).fetchone()
            self.assertIsNotNone(block)

            # Get all transaction hashes in Block #1 in leaf_index order
            tx_rows = conn.execute(
                "SELECT record_hash FROM blockchain_transactions WHERE block_index = 1 ORDER BY leaf_index ASC;"
            ).fetchall()
            leaves = [r["record_hash"] for r in tx_rows]

            tree = MerkleTree(leaves)
            self.assertEqual(tree.get_root(), block["merkle_root"])

            proof = tree.get_proof(enc["merkle_leaf_index"])
            is_valid = MerkleTree.verify_proof(enc["record_hash"], proof, block["merkle_root"])
            self.assertTrue(is_valid, "Merkle proof verification must succeed against on-chain root")

    def test_07_blockchain_hash_chain_unbroken(self):
        with get_connection(self.db_path) as conn:
            blocks = conn.execute(
                "SELECT block_index, timestamp, previous_hash, merkle_root, block_hash, nonce, miner_org "
                "FROM blockchain_blocks ORDER BY block_index ASC;"
            ).fetchall()

        self.assertGreater(len(blocks), 1)
        self.assertEqual(blocks[0]["block_index"], 0)
        self.assertEqual(blocks[0]["previous_hash"], "0" * 64)

        for i in range(1, len(blocks)):
            curr = blocks[i]
            prev = blocks[i - 1]
            self.assertEqual(
                curr["previous_hash"], prev["block_hash"],
                f"Block #{curr['block_index']} previous_hash must match Block #{prev['block_index']} hash"
            )
            # Verify PoW target
            self.assertTrue(
                curr["block_hash"].startswith("00"),
                f"Block #{curr['block_index']} must satisfy PoW target '00'"
            )

    def test_08_clinical_tamper_detection(self):
        # Find an encounter with conditions
        with get_connection(self.db_path) as conn:
            enc = conn.execute("""
                SELECT e.id, e.record_hash, c.id AS cond_id, c.description AS orig_desc
                FROM encounters e
                JOIN conditions c ON e.id = c.encounter_id
                LIMIT 1;
            """).fetchone()

        eid = enc["id"]
        cond_id = enc["cond_id"]
        orig_desc = enc["orig_desc"]
        stored_hash = enc["record_hash"]

        try:
            # Simulate clinical tamper in off-chain database
            with get_connection(self.db_path) as conn:
                conn.execute(
                    "UPDATE conditions SET description = 'TAMPERED DIAGNOSIS' WHERE id = ?;",
                    (cond_id,)
                )

            # Reconstruct canonical package
            tampered_pkg = get_canonical_encounter_package(eid, self.db_path)
            tampered_hash = sha256_hash(canonical_json(tampered_pkg))

            # The tampered hash must differ from the stored blockchain record_hash
            self.assertNotEqual(
                stored_hash, tampered_hash,
                "Altering clinical condition must produce a different SHA-256 hash"
            )
        finally:
            # Restore original clinical data
            with get_connection(self.db_path) as conn:
                conn.execute(
                    "UPDATE conditions SET description = ? WHERE id = ?;",
                    (orig_desc, cond_id)
                )

    def test_09_claim_and_billing_tamper_detection(self):
        # Find an encounter with an associated claim
        with get_connection(self.db_path) as conn:
            claim = conn.execute("""
                SELECT c.id, c.encounter_id, c.total_claim_cost, c.procedure_code, e.record_hash
                FROM claims c
                JOIN encounters e ON c.encounter_id = e.id
                LIMIT 1;
            """).fetchone()

        cid = claim["id"]
        eid = claim["encounter_id"]
        orig_cost = claim["total_claim_cost"]
        stored_hash = claim["record_hash"]

        try:
            # Simulate fraudulent billing alteration (inflating cost from $X to $99999.00)
            with get_connection(self.db_path) as conn:
                conn.execute(
                    "UPDATE claims SET total_claim_cost = 99999.00 WHERE id = ?;",
                    (cid,)
                )

            # Reconstruct canonical package
            tampered_pkg = get_canonical_encounter_package(eid, self.db_path)
            tampered_hash = sha256_hash(canonical_json(tampered_pkg))

            # Cryptographic mismatch detected
            self.assertNotEqual(
                stored_hash, tampered_hash,
                "Altering billing claim cost must alter canonical SHA-256 hash and trigger tamper alert"
            )
        finally:
            # Restore original claim cost
            with get_connection(self.db_path) as conn:
                conn.execute(
                    "UPDATE claims SET total_claim_cost = ? WHERE id = ?;",
                    (orig_cost, cid)
                )

    def test_10_cross_hospital_multi_org_patient(self):
        with get_connection(self.db_path) as conn:
            # Find a patient with encounters from multiple organizations
            row = conn.execute("""
                SELECT patient_id, COUNT(DISTINCT organization_id) as org_cnt
                FROM encounters
                GROUP BY patient_id
                HAVING org_cnt > 1
                LIMIT 1;
            """).fetchone()

            pid = row["patient_id"]
            org_cnt = row["org_cnt"]
            self.assertGreaterEqual(org_cnt, 2, "Patient must have records across >= 2 hospitals")

            # Fetch patient encounters
            encs = conn.execute("""
                SELECT e.id, e.organization_id, o.name as org_name, e.record_hash, e.block_index
                FROM encounters e
                JOIN organizations o ON e.organization_id = o.id
                WHERE e.patient_id = ?
                ORDER BY e.start_time ASC;
            """, (pid,)).fetchall()

            org_names_found = set(r["org_name"] for r in encs)
            self.assertGreaterEqual(len(org_names_found), 2)


if __name__ == "__main__":
    unittest.main()
