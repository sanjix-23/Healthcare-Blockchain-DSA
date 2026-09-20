"""
Comprehensive Automated Test Suite for Phase 3: Backend REST API.

Tests:
1. System Root Status (/): Checks health and patient/blockchain metrics.
2. Organization Authentication (/api/auth/login): Validates hospital, insurance, and admin logins.
3. Patient Login Prohibition: Proves patient login is rejected with HTTP 403.
4. Patient Search (/api/patients/search): Tests O(1) ID and substring name searches.
5. Privacy & Data Minimization: Ensures SSN, passport, driver's license, lat/lon are not exposed.
6. Longitudinal EHR Retrieval (/api/patients/{id}/ehr): Verifies complete multi-hospital timeline.
7. Cross-Hospital Data Retrieval: Demonstrates Hospital B retrieving records originating from Hospital A.
8. Zero-Trust Integrity Verification (/api/encounters/{id}/verify): Confirms untampered record is VERIFIED.
9. Clinical Tamper Detection: Proves modifying a clinical diagnosis triggers RED ALERT (TAMPERED).
10. Claim & Billing Tamper Detection: Proves modifying a claim billing field triggers TAMPERED alert.
11. Dynamic Patient Registration (/api/patients): Tests sequential ID generation (P001164+).
12. Dynamic Encounter Creation & Anchoring (/api/encounters): Tests SHA-256 -> Merkle Tree -> Mining -> Verification.
13. Blockchain Ledger Validation (/api/blockchain/validate): Tests full-chain cryptographic audit endpoint.
14. Audit Trail Stream (/api/audit): Verifies immutable event logging via custom linked list.
15. Performance Benchmark API (/api/performance/benchmark): Tests live micro-benchmark metrics.
"""

import unittest
from starlette.testclient import TestClient
from backend.app import app
from backend.state import AppState
from db.database import get_connection


class TestBackendAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Initialize app and client
        state = AppState.get_instance()
        state.initialize()
        cls.client = TestClient(app)

    def test_01_root_endpoint(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "OPERATIONAL")
        self.assertGreaterEqual(data["patients_indexed"], 1163)
        self.assertGreaterEqual(data["blockchain_height"], 124)
        self.assertFalse(data["patient_login_supported"])

    def test_02_organization_logins(self):
        # Hospital A login
        resp_a = self.client.post("/api/auth/login", json={"username": "hospital_a", "password": "hospital_a_pass"})
        self.assertEqual(resp_a.status_code, 200)
        self.assertEqual(resp_a.json()["role"], "HOSPITAL")

        # Hospital B login
        resp_b = self.client.post("/api/auth/login", json={"username": "hospital_b", "password": "hospital_b_pass"})
        self.assertEqual(resp_b.status_code, 200)
        self.assertEqual(resp_b.json()["role"], "HOSPITAL")

        # Insurance login
        resp_ins = self.client.post("/api/auth/login", json={"username": "insurance_bcbs", "password": "insurance_pass"})
        self.assertEqual(resp_ins.status_code, 200)
        self.assertEqual(resp_ins.json()["role"], "INSURANCE")

        # Admin login
        resp_admin = self.client.post("/api/auth/login", json={"username": "admin", "password": "admin_pass"})
        self.assertEqual(resp_admin.status_code, 200)
        self.assertEqual(resp_admin.json()["role"], "ADMIN")

    def test_03_patient_login_prohibited(self):
        resp = self.client.post("/api/auth/login", json={"username": "patient_john", "password": "any_password"})
        self.assertEqual(resp.status_code, 403)
        self.assertIn("Patient logins are not supported", resp.json()["detail"])

    def test_04_patient_search(self):
        # Search by ID
        resp_id = self.client.get("/api/patients/search?q=b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85")
        self.assertEqual(resp_id.status_code, 200)
        results = resp_id.json()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85")
        self.assertIn("organizations_visited", results[0])

        # Search by partial name
        resp_name = self.client.get("/api/patients/search?q=Damon")
        self.assertEqual(resp_name.status_code, 200)
        self.assertGreaterEqual(len(resp_name.json()), 1)

    def test_05_data_minimization_privacy(self):
        resp = self.client.get("/api/patients/search?limit=10")
        self.assertEqual(resp.status_code, 200)
        patients = resp.json()
        
        forbidden_keys = {"ssn", "drivers", "passport", "address", "lat", "lon", "maiden"}
        for p in patients:
            keys_lower = set(k.lower() for k in p.keys())
            self.assertTrue(keys_lower.isdisjoint(forbidden_keys), f"Exposed sensitive fields: {keys_lower & forbidden_keys}")

    def test_06_longitudinal_ehr_retrieval(self):
        pid = "b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85"
        resp = self.client.get(f"/api/patients/{pid}/ehr")
        self.assertEqual(resp.status_code, 200)
        ehr = resp.json()
        self.assertEqual(ehr["patient"]["id"], pid)
        self.assertGreater(ehr["encounter_count"], 0)

        first_enc = ehr["encounters"][0]
        self.assertIn("encounter_id", first_enc)
        self.assertIn("organization_id", first_enc)
        self.assertIn("record_hash", first_enc)
        self.assertIn("conditions", first_enc)
        self.assertIn("medications", first_enc)
        self.assertIn("procedures", first_enc)
        self.assertIn("observations", first_enc)
        self.assertIn("immunizations", first_enc)
        self.assertIn("claims", first_enc)

    def test_07_cross_hospital_data_retrieval(self):
        with get_connection() as conn:
            row = conn.execute("""
                SELECT patient_id FROM encounters
                GROUP BY patient_id HAVING COUNT(DISTINCT organization_id) > 1 LIMIT 1;
            """).fetchone()

        pid = row["patient_id"]
        # Hospital B retrieves patient EHR
        resp = self.client.get(f"/api/patients/{pid}/ehr?requesting_org=HOSPITAL_B")
        self.assertEqual(resp.status_code, 200)
        ehr = resp.json()

        org_ids = set(enc["organization_id"] for enc in ehr["encounters"])
        self.assertGreaterEqual(len(org_ids), 2, "Cross-hospital EHR must contain encounters from multiple hospitals")

    def test_08_integrity_verification_untampered(self):
        with get_connection() as conn:
            enc = conn.execute("SELECT id FROM encounters WHERE block_index = 1 LIMIT 1;").fetchone()

        eid = enc["id"]
        resp = self.client.get(f"/api/encounters/{eid}/verify?verifying_org=HOSPITAL_B")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        self.assertEqual(data["integrity_status"], "VERIFIED")
        self.assertTrue(data["hash_match"])
        self.assertTrue(data["merkle_proof_valid"])
        self.assertTrue(data["blockchain_valid"])
        self.assertEqual(data["current_hash"], data["stored_hash"])
        self.assertGreater(len(data["merkle_proof"]), 0)

    def test_09_clinical_tamper_detection(self):
        with get_connection() as conn:
            enc = conn.execute("""
                SELECT e.id FROM encounters e
                JOIN conditions c ON e.id = c.encounter_id LIMIT 1;
            """).fetchone()

        eid = enc["id"]

        # 1. Simulate clinical tampering
        tamper_resp = self.client.post("/api/tamper/clinical", json={
            "encounter_id": eid,
            "new_value": "MALICIOUSLY ALTERED DIAGNOSIS: CARDIAC ARREST"
        })
        self.assertEqual(tamper_resp.status_code, 200)

        # 2. Run integrity verification
        verif_resp = self.client.get(f"/api/encounters/{eid}/verify?verifying_org=HOSPITAL_B")
        self.assertEqual(verif_resp.status_code, 200)
        verif_data = verif_resp.json()

        self.assertEqual(verif_data["integrity_status"], "TAMPERED")
        self.assertFalse(verif_data["hash_match"])
        self.assertFalse(verif_data["merkle_proof_valid"])
        self.assertIsNotNone(verif_data["tamper_details"])

        # 3. Restore record
        restore_resp = self.client.post("/api/tamper/restore", json={"encounter_id": eid})
        self.assertEqual(restore_resp.status_code, 200)

        # 4. Verify record is restored to VERIFIED status
        restored_verif = self.client.get(f"/api/encounters/{eid}/verify?verifying_org=HOSPITAL_B")
        self.assertEqual(restored_verif.json()["integrity_status"], "VERIFIED")

    def test_10_claim_and_billing_tamper_detection(self):
        with get_connection() as conn:
            claim = conn.execute("SELECT id, encounter_id FROM claims LIMIT 1;").fetchone()

        cid = claim["id"]
        eid = claim["encounter_id"]

        # 1. Simulate fraudulent billing alteration
        tamper_resp = self.client.post("/api/tamper/billing", json={
            "encounter_id": eid,
            "field": "total_claim_cost",
            "new_value": 77777.77
        })
        self.assertEqual(tamper_resp.status_code, 200)

        # 2. Verify via insurance claim verification endpoint
        verif_resp = self.client.get(f"/api/claims/{cid}/verify?verifying_payer=INSURANCE_BCBS")
        self.assertEqual(verif_resp.status_code, 200)
        verif_data = verif_resp.json()

        self.assertFalse(verif_data["billing_integrity_verified"])
        self.assertEqual(verif_data["verification_details"]["integrity_status"], "TAMPERED")

        # 3. Restore billing data
        restore_resp = self.client.post("/api/tamper/restore", json={"encounter_id": eid})
        self.assertEqual(restore_resp.status_code, 200)

        # 4. Verify billing claim returns to verified
        restored_verif = self.client.get(f"/api/claims/{cid}/verify?verifying_payer=INSURANCE_BCBS")
        self.assertTrue(restored_verif.json()["billing_integrity_verified"])

    def test_11_register_new_patient(self):
        new_patient_payload = {
            "first_name": "TestDynamicFirst",
            "last_name": "TestDynamicLast",
            "birthdate": "1995-04-20",
            "gender": "F",
            "city": "Boston",
            "state": "Massachusetts",
            "zip": "02115"
        }
        resp = self.client.post("/api/patients", json=new_patient_payload)
        self.assertEqual(resp.status_code, 201)
        data = resp.json()

        self.assertTrue(data["patient_id"].startswith("P"))
        new_pid = data["patient_id"]

        # Verify immediately searchable via CustomHashTable
        search_resp = self.client.get(f"/api/patients/search?q={new_pid}")
        self.assertEqual(search_resp.status_code, 200)
        self.assertEqual(len(search_resp.json()), 1)
        self.assertEqual(search_resp.json()[0]["first_name"], "TestDynamicFirst")

    def test_12_add_new_encounter_and_verify(self):
        # Register a fresh patient
        p_resp = self.client.post("/api/patients", json={
            "first_name": "DynamicEncounter",
            "last_name": "Patient",
            "birthdate": "1988-11-03",
            "gender": "M",
            "city": "Cambridge",
            "state": "Massachusetts",
            "zip": "02138"
        })
        pid = p_resp.json()["patient_id"]

        # Add an encounter
        enc_payload = {
            "patient_id": pid,
            "organization_id": "6f122869-a856-3d65-8db9-099bf4f5bbb8",  # Hospital A
            "encounter_class": "ambulatory",
            "description": "Acute Bronchitis Evaluation",
            "base_cost": 175.50,
            "conditions": [{"code": "10509002", "description": "Acute bronchitis (disorder)"}],
            "medications": [{"code": "313782", "description": "Acetaminophen 325 MG Oral Tablet", "dispenses": 30, "total_cost": 15.0}],
            "observations": [{"category": "vital-signs", "code": "8480-6", "description": "Systolic Blood Pressure", "value": "120", "units": "mm[Hg]"}],
            "claim": {
                "total_claim_cost": 175.50,
                "payer_coverage": 150.0,
                "diagnosis_code": "10509002",
                "procedure_code": "GENERAL_VISIT",
                "status": "CLOSED"
            }
        }
        enc_resp = self.client.post("/api/encounters", json=enc_payload)
        self.assertEqual(enc_resp.status_code, 201)
        enc_data = enc_resp.json()

        eid = enc_data["encounter_id"]
        self.assertEqual(enc_data["status"], "ANCHORED")
        self.assertGreater(enc_data["block_index"], 123)
        self.assertEqual(len(enc_data["record_hash"]), 64)

        # Verify immediately
        verif_resp = self.client.get(f"/api/encounters/{eid}/verify?verifying_org=HOSPITAL_B")
        self.assertEqual(verif_resp.status_code, 200)
        self.assertEqual(verif_resp.json()["integrity_status"], "VERIFIED")
        self.assertTrue(verif_resp.json()["hash_match"])
        self.assertTrue(verif_resp.json()["merkle_proof_valid"])
        self.assertTrue(verif_resp.json()["blockchain_valid"])

    def test_13_blockchain_validation_endpoint(self):
        resp = self.client.get("/api/blockchain/validate")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["is_valid"])
        self.assertEqual(data["status"], "VALID")
        self.assertGreaterEqual(data["total_blocks_verified"], 124)

    def test_14_audit_log_stream(self):
        resp = self.client.get("/api/audit?limit=10")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertGreater(data["event_count"], 0)
        self.assertIn("events", data)

    def test_15_performance_benchmark_endpoint(self):
        resp = self.client.get("/api/performance/benchmark")
        self.assertEqual(resp.status_code, 200)
        bench = resp.json()["benchmarks"]
        self.assertIn("sha256_microsecond", bench)
        self.assertIn("merkle_construction", bench)
        self.assertIn("merkle_proof_generation_us", bench)
        self.assertIn("merkle_proof_verification_us", bench)
        self.assertIn("hash_table_lookup_us", bench)
        self.assertIn("blockchain_validation_ms", bench)


if __name__ == "__main__":
    unittest.main()
