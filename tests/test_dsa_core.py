"""
Unit Tests for Phase 1 Core DSA Implementations.

Tests cover:
1. SHA-256 consistency and canonical JSON serialization
2. Merkle Tree root generation (even, odd, single, empty leaves)
3. Merkle proof generation for all leaves
4. Merkle proof verification
5. Invalid Merkle proof detection (tampered hash, corrupted sibling)
6. Blockchain previous_hash linking and PoW mining
7. Blockchain tampering detection (altered transaction, broken previous_hash)
8. Custom Hash Table insert/get/delete
9. Custom Hash Table collision handling and rehashing
10. Linked List append and sequential chronological traversal
"""

import unittest
from core.crypto import sha256_hash, canonical_json, hash_record
from core.merkle_tree import MerkleTree
from core.blockchain import Blockchain, Block
from core.hash_table import CustomHashTable
from core.linked_list import PatientHistoryLinkedList, HistoryNode


class TestDSACore(unittest.TestCase):

    # ==========================================
    # 1. SHA-256 & Canonical JSON Tests
    # ==========================================
    def test_sha256_consistency(self):
        h1 = sha256_hash("Healthcare Record 101")
        h2 = sha256_hash("Healthcare Record 101")
        h3 = sha256_hash("Healthcare Record 102")
        self.assertEqual(h1, h2, "SHA-256 must be deterministic")
        self.assertNotEqual(h1, h3, "Different inputs must produce different hashes")
        self.assertEqual(len(h1), 64, "SHA-256 digest must be exactly 64 hex characters")

    def test_canonical_json_key_order_invariance(self):
        dict1 = {"patient_id": "P001", "cost": 150.0, "diagnosis": "Hypertension"}
        dict2 = {"diagnosis": "Hypertension", "cost": 150.0, "patient_id": "P001"}
        self.assertEqual(canonical_json(dict1), canonical_json(dict2), "Key ordering must not alter canonical JSON")
        self.assertEqual(hash_record(dict1), hash_record(dict2), "Reordered dictionary keys must produce identical hash")

    # ==========================================
    # 2. Merkle Tree Tests
    # ==========================================
    def test_merkle_root_generation(self):
        # 4 leaves (Power of 2)
        leaves = [sha256_hash(f"record_{i}") for i in range(4)]
        tree = MerkleTree(leaves)
        root = tree.get_root()
        self.assertEqual(len(root), 64)

        # Manually compute expected root
        h01 = sha256_hash(leaves[0] + leaves[1])
        h23 = sha256_hash(leaves[2] + leaves[3])
        expected_root = sha256_hash(h01 + h23)
        self.assertEqual(root, expected_root, "Merkle root must match manual bottom-up calculation")

    def test_merkle_root_odd_leaves(self):
        # 3 leaves (Odd count: 3rd leaf is duplicated)
        leaves = [sha256_hash(f"rec_{i}") for i in range(3)]
        tree = MerkleTree(leaves)
        root = tree.get_root()

        h01 = sha256_hash(leaves[0] + leaves[1])
        h22 = sha256_hash(leaves[2] + leaves[2])
        expected_root = sha256_hash(h01 + h22)
        self.assertEqual(root, expected_root, "Odd leaf count must correctly duplicate final leaf")

    def test_merkle_proof_generation_and_verification(self):
        # Test with 7 leaves (odd and multi-level)
        leaves = [sha256_hash(f"clinical_package_{i}") for i in range(7)]
        tree = MerkleTree(leaves)
        root = tree.get_root()

        for idx in range(len(leaves)):
            proof = tree.get_proof(idx)
            is_valid = MerkleTree.verify_proof(leaves[idx], proof, root)
            self.assertTrue(is_valid, f"Proof verification failed for leaf index {idx}")

    def test_invalid_merkle_proof_detection(self):
        leaves = [sha256_hash(f"record_{i}") for i in range(4)]
        tree = MerkleTree(leaves)
        root = tree.get_root()

        proof = tree.get_proof(0)
        tampered_leaf = sha256_hash("tampered_record_0")

        # Verifying with tampered leaf must fail
        self.assertFalse(
            MerkleTree.verify_proof(tampered_leaf, proof, root),
            "Merkle proof must reject tampered leaf hash"
        )

        # Verifying against wrong root must fail
        wrong_root = sha256_hash("wrong_merkle_root")
        self.assertFalse(
            MerkleTree.verify_proof(leaves[0], proof, wrong_root),
            "Merkle proof must reject wrong root"
        )

    # ==========================================
    # 3. Blockchain Tests
    # ==========================================
    def test_blockchain_genesis_and_linking(self):
        bc = Blockchain(difficulty=2)
        genesis = bc.create_genesis_block()
        self.assertEqual(genesis.index, 0)
        self.assertEqual(genesis.previous_hash, "0" * 64)
        self.assertTrue(genesis.block_hash.startswith("00"))

        # Add Block 1
        txs_b1 = [{"record_id": "r1", "record_hash": sha256_hash("tx1")}]
        b1 = bc.add_block(txs_b1, miner_org="HOSPITAL_A")
        self.assertEqual(b1.index, 1)
        self.assertEqual(b1.previous_hash, genesis.block_hash)
        self.assertTrue(b1.block_hash.startswith("00"))

        # Add Block 2
        txs_b2 = [{"record_id": "r2", "record_hash": sha256_hash("tx2")}]
        b2 = bc.add_block(txs_b2, miner_org="HOSPITAL_B")
        self.assertEqual(b2.index, 2)
        self.assertEqual(b2.previous_hash, b1.block_hash)

        # Verify chain integrity
        valid, msg = bc.is_valid_chain()
        self.assertTrue(valid, msg)

    def test_blockchain_tampering_detection(self):
        bc = Blockchain(difficulty=2)
        bc.create_genesis_block()
        
        txs_b1 = [{"record_id": "r1", "record_hash": sha256_hash("tx1")}]
        b1 = bc.add_block(txs_b1, miner_org="HOSPITAL_A")
        
        txs_b2 = [{"record_id": "r2", "record_hash": sha256_hash("tx2")}]
        bc.add_block(txs_b2, miner_org="HOSPITAL_B")

        valid, _ = bc.is_valid_chain()
        self.assertTrue(valid)

        # Tamper 1: Modify transaction payload in Block 1
        b1.transactions[0]["record_hash"] = sha256_hash("tampered_tx1")
        valid, err = bc.is_valid_chain()
        self.assertFalse(valid, "Tampered transaction must invalidate Merkle root check")
        self.assertIn("Merkle root mismatch", err)

        # Restore transaction and tamper with header previous_hash
        b1.transactions[0]["record_hash"] = sha256_hash("tx1")
        b1.previous_hash = sha256_hash("corrupted_previous_hash")
        valid, err = bc.is_valid_chain()
        self.assertFalse(valid, "Corrupted previous_hash must break hash-linked chain")

    # ==========================================
    # 4. Custom Hash Table Tests
    # ==========================================
    def test_hash_table_basic_operations(self):
        ht = CustomHashTable(initial_capacity=16)
        ht.put("P001", {"name": "Alice", "age": 30})
        ht.put("P002", {"name": "Bob", "age": 45})

        self.assertEqual(len(ht), 2)
        self.assertEqual(ht.get("P001")["name"], "Alice")
        self.assertEqual(ht.get("P002")["name"], "Bob")
        self.assertIsNone(ht.get("P999"))

        # Update existing key
        ht.put("P001", {"name": "Alice Smith", "age": 31})
        self.assertEqual(len(ht), 2)
        self.assertEqual(ht.get("P001")["name"], "Alice Smith")

        # Delete key
        deleted = ht.delete("P002")
        self.assertTrue(deleted)
        self.assertEqual(len(ht), 1)
        self.assertIsNone(ht.get("P002"))

    def test_hash_table_collisions_and_rehashing(self):
        # Force small initial capacity to test collisions and dynamic resizing
        ht = CustomHashTable(initial_capacity=8)
        
        # Insert 100 items to force multiple resizes and collision chaining
        for i in range(100):
            ht.put(f"patient_uuid_{i}", f"record_data_{i}")

        self.assertEqual(len(ht), 100)
        self.assertGreater(ht.capacity, 8, "Hash table must have resized dynamically")

        # Verify all 100 items are retrievable
        for i in range(100):
            val = ht.get(f"patient_uuid_{i}")
            self.assertEqual(val, f"record_data_{i}")

        diagnostics = ht.get_diagnostics()
        self.assertLessEqual(diagnostics["load_factor"], 0.75, "Load factor must remain <= 0.75")

    # ==========================================
    # 5. Linked List Tests
    # ==========================================
    def test_linked_list_append_and_traversal(self):
        history = PatientHistoryLinkedList()
        self.assertEqual(len(history), 0)

        # Append Encounter 1 (Hospital A)
        node1 = HistoryNode(
            encounter_id="enc-01",
            patient_id="P001",
            organization_id="HOSPITAL_A",
            provider_id="DOC_A",
            start_time="2024-01-10T10:00:00Z",
            stop_time="2024-01-10T10:30:00Z",
            encounter_class="ambulatory",
            description="Annual Physical",
            base_cost=100.0,
            record_hash=sha256_hash("enc-01-data")
        )
        history.append(node1)

        # Append Encounter 2 (Hospital B)
        node2 = HistoryNode(
            encounter_id="enc-02",
            patient_id="P001",
            organization_id="HOSPITAL_B",
            provider_id="DOC_B",
            start_time="2024-06-15T14:00:00Z",
            stop_time="2024-06-15T14:45:00Z",
            encounter_class="emergency",
            description="Chest Pain Evaluation",
            base_cost=450.0,
            record_hash=sha256_hash("enc-02-data")
        )
        history.append(node2)

        self.assertEqual(len(history), 2)

        # Chronological traversal
        enc_list = history.to_list()
        self.assertEqual(len(enc_list), 2)
        self.assertEqual(enc_list[0]["encounter_id"], "enc-01")
        self.assertEqual(enc_list[0]["organization_id"], "HOSPITAL_A")
        self.assertEqual(enc_list[1]["encounter_id"], "enc-02")
        self.assertEqual(enc_list[1]["organization_id"], "HOSPITAL_B")

        # Find by ID
        found = history.find("enc-02")
        self.assertIsNotNone(found)
        self.assertEqual(found.description, "Chest Pain Evaluation")
        self.assertIsNone(history.find("enc-999"))


if __name__ == "__main__":
    unittest.main()
