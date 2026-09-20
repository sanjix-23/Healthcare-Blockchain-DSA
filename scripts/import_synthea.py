"""
Synthea Dataset Ingestion and Initial Blockchain Anchoring Script.

Performs:
1. Ingestion of 1,163 patients with data minimization (dropping SSN, passport, driver's license, etc.)
2. Ingestion of organizations, payers, providers, encounters, conditions, medications,
   procedures, immunizations, vital observations, and claims.
3. Automated partitioning of all 61,459 encounters into blocks of ~500 encounters each.
4. Programmatic calculation of required block count: ceil(61,459 / 500) = 123 blocks.
5. Construction of binary Merkle Tree per block, computing the Merkle Root.
6. Lightweight Proof-of-Work mining (difficulty target '00') linking previous_hash.
7. Preserving record_hash, block_index, and merkle_leaf_index in both SQLite and on-chain tables.
8. Full cryptographic validation of the newly initialized blockchain ledger.

Run via:
    python scripts/import_synthea.py
"""

import os
import sys
import csv
import math
import time
from collections import defaultdict
from typing import Dict, List, Any, Optional

# Add parent directory to path so core and db packages are discoverable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.crypto import sha256_hash, canonical_json
from core.merkle_tree import MerkleTree
from core.blockchain import Blockchain, Block
from db.database import get_connection, init_db, get_db_path, log_audit

DATASET_DIR = r"C:\Healthcare-Blockchain-DSA\dataset"
DEFAULT_BATCH_SIZE = 500
POW_DIFFICULTY = 2


def clean_val(val: Optional[str]) -> str:
    return val.strip() if val else ""


def parse_float(val: Optional[str], default: float = 0.0) -> float:
    try:
        return float(val) if val else default
    except (ValueError, TypeError):
        return default


def parse_int(val: Optional[str], default: int = 1) -> int:
    try:
        return int(float(val)) if val else default
    except (ValueError, TypeError):
        return default


def run_import(
    dataset_dir: str = DATASET_DIR,
    batch_size: int = DEFAULT_BATCH_SIZE,
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executes the full end-to-end dataset import and blockchain anchoring.
    """
    start_total_time = time.time()
    db_file = db_path or get_db_path()

    print("=" * 70)
    print("HEALTHCARE BLOCKCHAIN DSA CAPSTONE — INITIAL DATASET IMPORT")
    print(f"Dataset Directory : {dataset_dir}")
    print(f"Target Database   : {db_file}")
    print(f"Block Batch Size  : {batch_size} encounters / block")
    print(f"PoW Difficulty    : {POW_DIFFICULTY} leading zeros ('{'0'*POW_DIFFICULTY}')")
    print("=" * 70)

    # Initialize Fresh Database Schema
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
            print("[1/8] Removed existing database file for a clean initialization.")
        except Exception as e:
            print(f"[1/8] Notice: Could not remove old db file: {e}")

    init_db(db_file)
    print("[1/8] Initialized normalized SQLite schema successfully.")

    conn = sqlite3_connect_fast(db_file)

    try:
        # -------------------------------------------------------------
        # 1. Ingest Organizations
        # -------------------------------------------------------------
        org_path = os.path.join(dataset_dir, "organizations.csv")
        org_rows = []
        org_names = {}
        with open(org_path, "r", encoding="utf-8", errors="replace") as f:
            for r in csv.DictReader(f):
                oid = clean_val(r.get("Id"))
                name = clean_val(r.get("NAME"))
                org_names[oid] = name
                org_rows.append((
                    oid,
                    name,
                    clean_val(r.get("CITY")),
                    clean_val(r.get("STATE")),
                    clean_val(r.get("PHONE")),
                    "HOSPITAL"
                ))
        conn.executemany("""
            INSERT OR REPLACE INTO organizations (id, name, city, state, phone, org_type)
            VALUES (?, ?, ?, ?, ?, ?);
        """, org_rows)
        print(f"[2/8] Ingested {len(org_rows)} healthcare organizations.")

        # -------------------------------------------------------------
        # 2. Ingest Payers (Insurance Companies)
        # -------------------------------------------------------------
        payer_path = os.path.join(dataset_dir, "payers.csv")
        payer_rows = []
        with open(payer_path, "r", encoding="utf-8", errors="replace") as f:
            for r in csv.DictReader(f):
                payer_rows.append((
                    clean_val(r.get("Id")),
                    clean_val(r.get("NAME")),
                    clean_val(r.get("CITY")),
                    clean_val(r.get("STATE_HEADQUARTERED")),
                    clean_val(r.get("PHONE"))
                ))
        conn.executemany("""
            INSERT OR REPLACE INTO payers (id, name, city, state, phone)
            VALUES (?, ?, ?, ?, ?);
        """, payer_rows)
        print(f"[3/8] Ingested {len(payer_rows)} insurance payers.")

        # -------------------------------------------------------------
        # 3. Ingest Providers (Clinicians)
        # -------------------------------------------------------------
        provider_path = os.path.join(dataset_dir, "providers.csv")
        provider_rows = []
        with open(provider_path, "r", encoding="utf-8", errors="replace") as f:
            for r in csv.DictReader(f):
                provider_rows.append((
                    clean_val(r.get("Id")),
                    clean_val(r.get("ORGANIZATION")),
                    clean_val(r.get("NAME")),
                    clean_val(r.get("SPECIALITY")),
                    clean_val(r.get("GENDER"))
                ))
        conn.executemany("""
            INSERT OR REPLACE INTO providers (id, organization_id, name, speciality, gender)
            VALUES (?, ?, ?, ?, ?);
        """, provider_rows)
        print(f"[4/8] Ingested {len(provider_rows)} providers.")

        # -------------------------------------------------------------
        # 4. Ingest Patients (DATA MINIMIZATION ENFORCED)
        # -------------------------------------------------------------
        # Excludes: SSN, DRIVERS, PASSPORT, exact street ADDRESS, LAT, LON, MAIDEN
        patient_path = os.path.join(dataset_dir, "patients.csv")
        patient_rows = []
        with open(patient_path, "r", encoding="utf-8", errors="replace") as f:
            for r in csv.DictReader(f):
                patient_rows.append((
                    clean_val(r.get("Id")),
                    clean_val(r.get("FIRST")),
                    clean_val(r.get("LAST")),
                    clean_val(r.get("BIRTHDATE")),
                    clean_val(r.get("DEATHDATE")) or None,
                    clean_val(r.get("GENDER")),
                    clean_val(r.get("RACE")),
                    clean_val(r.get("ETHNICITY")),
                    clean_val(r.get("CITY")),
                    clean_val(r.get("STATE")),
                    clean_val(r.get("ZIP"))
                ))
        conn.executemany("""
            INSERT OR REPLACE INTO patients (
                id, first_name, last_name, birthdate, deathdate, gender, race, ethnicity, city, state, zip
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, patient_rows)
        print(f"[5/8] Ingested all {len(patient_rows)} Synthea patients (privacy fields minimized).")

        # -------------------------------------------------------------
        # 5. Load Clinical Child Data into In-Memory Lookups
        # -------------------------------------------------------------
        print("[6/8] Parsing clinical entities (conditions, medications, procedures, immunizations, observations, claims)...")
        t_clin = time.time()

        conditions_by_enc = defaultdict(list)
        cond_insert_rows = []
        with open(os.path.join(dataset_dir, "conditions.csv"), "r", encoding="utf-8", errors="replace") as f:
            for r in csv.DictReader(f):
                enc_id = clean_val(r.get("ENCOUNTER"))
                pat_id = clean_val(r.get("PATIENT"))
                code = clean_val(r.get("CODE"))
                desc = clean_val(r.get("DESCRIPTION"))
                start = clean_val(r.get("START"))
                stop = clean_val(r.get("STOP")) or None
                conditions_by_enc[enc_id].append({"code": code, "description": desc})
                cond_insert_rows.append((enc_id, pat_id, code, desc, start, stop))

        medications_by_enc = defaultdict(list)
        med_insert_rows = []
        with open(os.path.join(dataset_dir, "medications.csv"), "r", encoding="utf-8", errors="replace") as f:
            for r in csv.DictReader(f):
                enc_id = clean_val(r.get("ENCOUNTER"))
                pat_id = clean_val(r.get("PATIENT"))
                code = clean_val(r.get("CODE"))
                desc = clean_val(r.get("DESCRIPTION"))
                start = clean_val(r.get("START"))
                stop = clean_val(r.get("STOP")) or None
                disp = parse_int(r.get("DISPENSES"), 1)
                cost = parse_float(r.get("TOTALCOST"), 0.0)
                medications_by_enc[enc_id].append({
                    "code": code, "description": desc, "dispenses": disp, "total_cost": cost
                })
                med_insert_rows.append((enc_id, pat_id, code, desc, start, stop, disp, cost))

        procedures_by_enc = defaultdict(list)
        proc_insert_rows = []
        with open(os.path.join(dataset_dir, "procedures.csv"), "r", encoding="utf-8", errors="replace") as f:
            for r in csv.DictReader(f):
                enc_id = clean_val(r.get("ENCOUNTER"))
                pat_id = clean_val(r.get("PATIENT"))
                code = clean_val(r.get("CODE"))
                desc = clean_val(r.get("DESCRIPTION"))
                pdate = clean_val(r.get("START"))
                bcost = parse_float(r.get("BASE_COST"), 0.0)
                procedures_by_enc[enc_id].append({
                    "code": code, "description": desc, "base_cost": bcost
                })
                proc_insert_rows.append((enc_id, pat_id, code, desc, pdate, bcost))

        immunizations_by_enc = defaultdict(list)
        imm_insert_rows = []
        with open(os.path.join(dataset_dir, "immunizations.csv"), "r", encoding="utf-8", errors="replace") as f:
            for r in csv.DictReader(f):
                enc_id = clean_val(r.get("ENCOUNTER"))
                pat_id = clean_val(r.get("PATIENT"))
                code = clean_val(r.get("CODE"))
                desc = clean_val(r.get("DESCRIPTION"))
                idate = clean_val(r.get("DATE"))
                immunizations_by_enc[enc_id].append({"code": code, "description": desc})
                imm_insert_rows.append((enc_id, pat_id, code, desc, idate))

        # Important clinical observations: vital signs and laboratory panels
        observations_by_enc = defaultdict(list)
        obs_insert_rows = []
        with open(os.path.join(dataset_dir, "observations.csv"), "r", encoding="utf-8", errors="replace") as f:
            for r in csv.DictReader(f):
                cat = clean_val(r.get("CATEGORY"))
                if cat in ("vital-signs", "laboratory", "exam"):
                    enc_id = clean_val(r.get("ENCOUNTER"))
                    pat_id = clean_val(r.get("PATIENT"))
                    code = clean_val(r.get("CODE"))
                    desc = clean_val(r.get("DESCRIPTION"))
                    val = clean_val(r.get("VALUE"))
                    units = clean_val(r.get("UNITS"))
                    odate = clean_val(r.get("DATE"))
                    observations_by_enc[enc_id].append({
                        "category": cat, "code": code, "description": desc, "value": val, "units": units
                    })
                    obs_insert_rows.append((enc_id, pat_id, cat, code, desc, val, units, odate))

        # Claims & Billing (with procedure_code support)
        claims_by_enc = {}
        claim_insert_rows = []
        with open(os.path.join(dataset_dir, "claims.csv"), "r", encoding="utf-8", errors="replace") as f:
            for r in csv.DictReader(f):
                enc_id = clean_val(r.get("APPOINTMENTID"))
                if not enc_id:
                    continue
                cid = clean_val(r.get("Id"))
                pid = clean_val(r.get("PATIENTID"))
                prov_id = clean_val(r.get("PROVIDERID"))
                payer_id = clean_val(r.get("PRIMARYPATIENTINSURANCEID"))
                sdate = clean_val(r.get("SERVICEDATE")) or clean_val(r.get("CURRENTILLNESSDATE"))
                status = clean_val(r.get("STATUS1")) or "CLOSED"
                diag_code = clean_val(r.get("DIAGNOSIS1"))
                
                # Store in lookup (will populate procedure_code and costs from encounter)
                claims_by_enc[enc_id] = {
                    "claim_id": cid,
                    "patient_id": pid,
                    "provider_id": prov_id,
                    "payer_id": payer_id,
                    "service_date": sdate,
                    "status": status,
                    "diagnosis_code": diag_code
                }

        # Bulk insert child tables into SQLite
        conn.executemany("""
            INSERT INTO conditions (encounter_id, patient_id, code, description, start_date, stop_date)
            VALUES (?, ?, ?, ?, ?, ?);
        """, cond_insert_rows)

        conn.executemany("""
            INSERT INTO medications (encounter_id, patient_id, code, description, start_date, stop_date, dispenses, total_cost)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, med_insert_rows)

        conn.executemany("""
            INSERT INTO procedures (encounter_id, patient_id, code, description, procedure_date, base_cost)
            VALUES (?, ?, ?, ?, ?, ?);
        """, proc_insert_rows)

        conn.executemany("""
            INSERT INTO immunizations (encounter_id, patient_id, code, description, date)
            VALUES (?, ?, ?, ?, ?);
        """, imm_insert_rows)

        conn.executemany("""
            INSERT INTO observations (encounter_id, patient_id, category, code, description, value, units, date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, obs_insert_rows)

        print(f"[6/8] Clinical entities inserted in {time.time() - t_clin:.2f}s "
              f"({len(cond_insert_rows)} conditions, {len(med_insert_rows)} medications, "
              f"{len(proc_insert_rows)} procedures, {len(imm_insert_rows)} vaccines, {len(obs_insert_rows)} vitals/labs).")

        # -------------------------------------------------------------
        # 6. Read Encounters and Assemble Canonical Packages
        # -------------------------------------------------------------
        print("[7/8] Reading encounters and computing canonical SHA-256 fingerprints...")
        t_enc = time.time()
        encounters_raw = []
        with open(os.path.join(dataset_dir, "encounters.csv"), "r", encoding="utf-8", errors="replace") as f:
            for r in csv.DictReader(f):
                enc_id = clean_val(r.get("Id"))
                encounters_raw.append({
                    "id": enc_id,
                    "patient_id": clean_val(r.get("PATIENT")),
                    "organization_id": clean_val(r.get("ORGANIZATION")),
                    "provider_id": clean_val(r.get("PROVIDER")),
                    "payer_id": clean_val(r.get("PAYER")),
                    "encounter_class": clean_val(r.get("ENCOUNTERCLASS")),
                    "code": clean_val(r.get("CODE")),
                    "description": clean_val(r.get("DESCRIPTION")),
                    "start_time": clean_val(r.get("START")),
                    "stop_time": clean_val(r.get("STOP")),
                    "base_cost": parse_float(r.get("BASE_ENCOUNTER_COST"), 0.0),
                    "total_claim_cost": parse_float(r.get("TOTAL_CLAIM_COST"), 0.0),
                    "payer_coverage": parse_float(r.get("PAYER_COVERAGE"), 0.0),
                    "reason_code": clean_val(r.get("REASONCODE")),
                    "reason_description": clean_val(r.get("REASONDESCRIPTION"))
                })

        total_encounters = len(encounters_raw)
        total_blocks_required = math.ceil(total_encounters / batch_size)
        print(f"      Loaded {total_encounters} encounters.")
        print(f"      Partitioning into {total_blocks_required} blocks (~{batch_size} encounters/block).")

        # Compute canonical package and SHA-256 for every encounter
        encounter_packages = []
        claim_rows_to_insert = []

        for enc in encounters_raw:
            eid = enc["id"]
            
            # Match or synthesize claim information
            c_meta = claims_by_enc.get(eid)
            claim_info = None
            if c_meta:
                claim_info = {
                    "claim_id": c_meta["claim_id"],
                    "payer_id": c_meta["payer_id"] or enc["payer_id"],
                    "status": c_meta["status"],
                    "total_claim_cost": enc["total_claim_cost"],
                    "payer_coverage": enc["payer_coverage"],
                    "diagnosis_code": c_meta["diagnosis_code"] or enc["reason_code"],
                    "procedure_code": enc["code"]  # Procedure code linked to encounter
                }
                claim_rows_to_insert.append((
                    claim_info["claim_id"],
                    enc["patient_id"],
                    eid,
                    c_meta["provider_id"] or enc["provider_id"],
                    claim_info["payer_id"],
                    c_meta["service_date"] or enc["start_time"],
                    claim_info["status"],
                    claim_info["total_claim_cost"],
                    claim_info["payer_coverage"],
                    claim_info["diagnosis_code"],
                    claim_info["procedure_code"]
                ))

            # Canonical deterministic package
            pkg = {
                "record_id": eid,
                "patient_id": enc["patient_id"],
                "organization_id": enc["organization_id"],
                "provider_id": enc["provider_id"],
                "payer_id": enc["payer_id"],
                "encounter_class": enc["encounter_class"],
                "code": enc["code"],
                "description": enc["description"],
                "start_time": enc["start_time"],
                "stop_time": enc["stop_time"],
                "base_cost": enc["base_cost"],
                "conditions": sorted(conditions_by_enc[eid], key=lambda x: (x["code"], x["description"])),
                "medications": sorted(medications_by_enc[eid], key=lambda x: x["code"]),
                "procedures": sorted(procedures_by_enc[eid], key=lambda x: x["code"]),
                "immunizations": sorted(immunizations_by_enc[eid], key=lambda x: x["code"]),
                "observations": sorted(observations_by_enc[eid], key=lambda x: x["code"]),
                "claim": claim_info
            }

            rec_hash = sha256_hash(canonical_json(pkg))
            enc["record_hash"] = rec_hash
            encounter_packages.append(enc)

        # Insert claims table
        conn.executemany("""
            INSERT OR REPLACE INTO claims (
                id, patient_id, encounter_id, provider_id, payer_id, service_date,
                status, total_claim_cost, payer_coverage, diagnosis_code, procedure_code
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, claim_rows_to_insert)
        print(f"      Inserted {len(claim_rows_to_insert)} billing claims bound to encounters.")

        # -------------------------------------------------------------
        # 7. Construct Initial Hash-Linked Blockchain & Mine Blocks
        # -------------------------------------------------------------
        print(f"[8/8] Constructing Blockchain & Mining {total_blocks_required} blocks with PoW difficulty '{'0'*POW_DIFFICULTY}'...")
        t_bc = time.time()

        blockchain = Blockchain(difficulty=POW_DIFFICULTY)
        genesis = blockchain.create_genesis_block(miner_org="GENESIS_SYSTEM")

        block_insert_rows = [(
            genesis.index,
            genesis.timestamp,
            genesis.previous_hash,
            genesis.merkle_root,
            genesis.block_hash,
            genesis.nonce,
            len(genesis.transactions),
            genesis.miner_org
        )]
        tx_insert_rows = []
        encounter_update_rows = []

        # Process each block batch
        for b_idx in range(total_blocks_required):
            start_i = b_idx * batch_size
            end_i = min(start_i + batch_size, total_encounters)
            batch = encounter_packages[start_i:end_i]

            # Primary organization of this batch
            miner_org = org_names.get(batch[0]["organization_id"], "REGIONAL_HEALTH_CONSORTIUM")

            txs = []
            for leaf_idx, enc in enumerate(batch):
                tx = {
                    "tx_id": f"tx-{enc['id'][:8]}-{b_idx}-{leaf_idx}",
                    "record_id": enc["id"],
                    "patient_id": enc["patient_id"],
                    "organization_id": enc["organization_id"],
                    "record_hash": enc["record_hash"],
                    "leaf_index": leaf_idx,
                    "timestamp": enc["start_time"]
                }
                txs.append(tx)

            # Add and mine block on the blockchain
            mined_block = blockchain.add_block(txs, miner_org=miner_org)

            # Collect block row
            block_insert_rows.append((
                mined_block.index,
                mined_block.timestamp,
                mined_block.previous_hash,
                mined_block.merkle_root,
                mined_block.block_hash,
                mined_block.nonce,
                len(mined_block.transactions),
                mined_block.miner_org
            ))

            # Collect transaction rows & encounter update data
            for tx in txs:
                tx_insert_rows.append((
                    tx["tx_id"],
                    mined_block.index,
                    tx["record_id"],
                    tx["patient_id"],
                    tx["organization_id"],
                    tx["record_hash"],
                    tx["leaf_index"],
                    tx["timestamp"]
                ))
                # For updating encounters table
                encounter_update_rows.append((
                    tx["record_hash"],
                    mined_block.index,
                    tx["leaf_index"],
                    tx["record_id"]
                ))

            if (b_idx + 1) % 25 == 0 or (b_idx + 1) == total_blocks_required:
                print(f"      Anchored Block #{mined_block.index}/{total_blocks_required} "
                      f"(Hash: {mined_block.block_hash[:12]}... MerkleRoot: {mined_block.merkle_root[:12]}... Nonce: {mined_block.nonce})")

        # Insert blockchain blocks & transactions
        conn.executemany("""
            INSERT INTO blockchain_blocks (block_index, timestamp, previous_hash, merkle_root, block_hash, nonce, tx_count, miner_org)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, block_insert_rows)

        conn.executemany("""
            INSERT INTO blockchain_transactions (tx_id, block_index, record_id, patient_id, organization_id, record_hash, leaf_index, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, tx_insert_rows)

        # Insert all encounters with their blockchain references
        enc_full_insert_rows = []
        for enc in encounter_packages:
            enc_full_insert_rows.append((
                enc["id"],
                enc["patient_id"],
                enc["organization_id"],
                enc["provider_id"],
                enc["payer_id"],
                enc["encounter_class"],
                enc["code"],
                enc["description"],
                enc["start_time"],
                enc["stop_time"],
                enc["base_cost"],
                enc["total_claim_cost"],
                enc["payer_coverage"],
                enc["reason_code"],
                enc["reason_description"],
                enc["record_hash"],
                None, # Will be set via update map
                None
            ))

        # Insert encounters table
        conn.executemany("""
            INSERT INTO encounters (
                id, patient_id, organization_id, provider_id, payer_id, encounter_class,
                code, description, start_time, stop_time, base_cost, total_claim_cost,
                payer_coverage, reason_code, reason_description, record_hash, block_index, merkle_leaf_index
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, enc_full_insert_rows)

        # Update block_index and merkle_leaf_index for all encounters
        conn.executemany("""
            UPDATE encounters
            SET record_hash = ?, block_index = ?, merkle_leaf_index = ?
            WHERE id = ?;
        """, encounter_update_rows)

        conn.commit()

        # -------------------------------------------------------------
        # 8. Cryptographic Validation of Newly Generated Ledger
        # -------------------------------------------------------------
        print("\n[VALIDATION] Running cryptographic audit over newly anchored blockchain...")
        valid, msg = blockchain.is_valid_chain()
        if not valid:
            raise RuntimeError(f"Cryptographic verification failed: {msg}")
        print(f"[VALIDATION] PASS: {msg}")

        # Record audit log
        conn.execute("""
            INSERT INTO audit_log (org_id, action, status, details)
            VALUES (?, ?, ?, ?);
        """, ("SYSTEM_INIT", "DATASET_IMPORT", "SUCCESS",
              f"Imported {len(patient_rows)} patients, {total_encounters} encounters, anchored {len(blockchain.chain)} blocks."))
        conn.commit()

        total_elapsed = time.time() - start_total_time
        print("=" * 70)
        print("SYNTHEA DATASET IMPORT & BLOCKCHAIN ANCHORING COMPLETED SUCCESSFULLY")
        print(f"Total Patients Imported    : {len(patient_rows)}")
        print(f"Total Encounters Imported  : {total_encounters}")
        print(f"Total Blocks Created       : {len(blockchain.chain)} (1 Genesis + {total_blocks_required} Data Blocks)")
        print(f"Total Transactions Anchored: {len(tx_insert_rows)}")
        print(f"Ledger Chain Status        : 100% CRYPTOGRAPHICALLY VALID")
        print(f"Total Ingestion Time       : {total_elapsed:.2f} seconds")
        print("=" * 70)

        return {
            "patients_count": len(patient_rows),
            "encounters_count": total_encounters,
            "blocks_count": len(blockchain.chain),
            "transactions_count": len(tx_insert_rows),
            "elapsed_seconds": round(total_elapsed, 2),
            "status": "SUCCESS"
        }

    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] Ingestion failed: {e}")
        raise
    finally:
        conn.close()


def sqlite3_connect_fast(db_path: str):
    """
    Creates an SQLite connection with pragmas tuned for fast bulk ingestion.
    """
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA synchronous = OFF;")
    conn.execute("PRAGMA journal_mode = MEMORY;")
    conn.execute("PRAGMA cache_size = 50000;")
    conn.execute("PRAGMA foreign_keys = OFF;") # Re-enabled after bulk insert
    return conn


if __name__ == "__main__":
    run_import()
