-- Database Schema for Healthcare Blockchain DSA Capstone Prototype
-- Storage Engine: SQLite 3

PRAGMA foreign_keys = ON;

-- 1. Patients Table (Demographic information minimized for security)
CREATE TABLE IF NOT EXISTS patients (
    id VARCHAR(64) PRIMARY KEY,
    first_name VARCHAR(64) NOT NULL,
    last_name VARCHAR(64) NOT NULL,
    birthdate DATE NOT NULL,
    deathdate DATE,
    gender VARCHAR(10),
    race VARCHAR(32),
    ethnicity VARCHAR(32),
    city VARCHAR(64),
    state VARCHAR(32),
    zip VARCHAR(16),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Organizations Table (Hospitals & Clinics)
CREATE TABLE IF NOT EXISTS organizations (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    city VARCHAR(64),
    state VARCHAR(32),
    phone VARCHAR(32),
    org_type VARCHAR(32) DEFAULT 'HOSPITAL'
);

-- 3. Payers Table (Health Insurance Companies)
CREATE TABLE IF NOT EXISTS payers (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    city VARCHAR(64),
    state VARCHAR(32),
    phone VARCHAR(32)
);

-- 4. Providers Table (Attending Clinicians)
CREATE TABLE IF NOT EXISTS providers (
    id VARCHAR(64) PRIMARY KEY,
    organization_id VARCHAR(64) REFERENCES organizations(id),
    name VARCHAR(128) NOT NULL,
    speciality VARCHAR(64),
    gender VARCHAR(10)
);

-- 5. Encounters Table (The Atomic EHR Clinical Package)
CREATE TABLE IF NOT EXISTS encounters (
    id VARCHAR(64) PRIMARY KEY,
    patient_id VARCHAR(64) NOT NULL REFERENCES patients(id),
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id),
    provider_id VARCHAR(64) REFERENCES providers(id),
    payer_id VARCHAR(64) REFERENCES payers(id),
    encounter_class VARCHAR(32) NOT NULL,
    code VARCHAR(32),
    description TEXT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    stop_time TIMESTAMP,
    base_cost DECIMAL(10,2) DEFAULT 0.0,
    total_claim_cost DECIMAL(10,2) DEFAULT 0.0,
    payer_coverage DECIMAL(10,2) DEFAULT 0.0,
    reason_code VARCHAR(32),
    reason_description TEXT,
    record_hash CHAR(64),
    block_index INTEGER,
    merkle_leaf_index INTEGER
);

-- 6. Claims Table (Billing & Claims with procedure_code added)
CREATE TABLE IF NOT EXISTS claims (
    id VARCHAR(64) PRIMARY KEY,
    patient_id VARCHAR(64) NOT NULL REFERENCES patients(id),
    encounter_id VARCHAR(64) REFERENCES encounters(id),
    provider_id VARCHAR(64) REFERENCES providers(id),
    payer_id VARCHAR(64) REFERENCES payers(id),
    service_date TIMESTAMP NOT NULL,
    status VARCHAR(32) DEFAULT 'CLOSED',
    total_claim_cost DECIMAL(10,2) NOT NULL DEFAULT 0.0,
    payer_coverage DECIMAL(10,2) NOT NULL DEFAULT 0.0,
    diagnosis_code VARCHAR(32),
    procedure_code VARCHAR(32)  -- Required for Claim Integrity Workflow
);

-- 7. Conditions Table (Diagnoses)
CREATE TABLE IF NOT EXISTS conditions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    encounter_id VARCHAR(64) NOT NULL REFERENCES encounters(id),
    patient_id VARCHAR(64) NOT NULL REFERENCES patients(id),
    code VARCHAR(32) NOT NULL,
    description TEXT NOT NULL,
    start_date DATE,
    stop_date DATE
);

-- 8. Medications Table (Prescriptions)
CREATE TABLE IF NOT EXISTS medications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    encounter_id VARCHAR(64) NOT NULL REFERENCES encounters(id),
    patient_id VARCHAR(64) NOT NULL REFERENCES patients(id),
    code VARCHAR(32) NOT NULL,
    description TEXT NOT NULL,
    start_date DATE,
    stop_date DATE,
    dispenses INTEGER DEFAULT 1,
    total_cost DECIMAL(10,2) DEFAULT 0.0
);

-- 9. Procedures Table (Clinical Interventions)
CREATE TABLE IF NOT EXISTS procedures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    encounter_id VARCHAR(64) NOT NULL REFERENCES encounters(id),
    patient_id VARCHAR(64) NOT NULL REFERENCES patients(id),
    code VARCHAR(32) NOT NULL,
    description TEXT NOT NULL,
    procedure_date TIMESTAMP,
    base_cost DECIMAL(10,2) DEFAULT 0.0
);

-- 10. Immunizations Table (Vaccines)
CREATE TABLE IF NOT EXISTS immunizations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    encounter_id VARCHAR(64) NOT NULL REFERENCES encounters(id),
    patient_id VARCHAR(64) NOT NULL REFERENCES patients(id),
    code VARCHAR(32) NOT NULL,
    description TEXT NOT NULL,
    date TIMESTAMP
);

-- 11. Observations Table (Vitals & Labs)
CREATE TABLE IF NOT EXISTS observations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    encounter_id VARCHAR(64) NOT NULL REFERENCES encounters(id),
    patient_id VARCHAR(64) NOT NULL REFERENCES patients(id),
    category VARCHAR(32),
    code VARCHAR(32) NOT NULL,
    description TEXT NOT NULL,
    value VARCHAR(64),
    units VARCHAR(32),
    date TIMESTAMP
);

-- 12. Blockchain Blocks Table (On-Chain Ledger Storage)
CREATE TABLE IF NOT EXISTS blockchain_blocks (
    block_index INTEGER PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    previous_hash CHAR(64) NOT NULL,
    merkle_root CHAR(64) NOT NULL,
    block_hash CHAR(64) NOT NULL,
    nonce INTEGER NOT NULL,
    tx_count INTEGER NOT NULL,
    miner_org VARCHAR(128) NOT NULL
);

-- 13. Blockchain Transactions Table (On-Chain Transaction Reference)
CREATE TABLE IF NOT EXISTS blockchain_transactions (
    tx_id VARCHAR(64) PRIMARY KEY,
    block_index INTEGER NOT NULL REFERENCES blockchain_blocks(block_index),
    record_id VARCHAR(64) NOT NULL,
    patient_id VARCHAR(64) NOT NULL,
    organization_id VARCHAR(64) NOT NULL,
    record_hash CHAR(64) NOT NULL,
    leaf_index INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL
);

-- 14. Audit Log Table (Immutable Append-Only Audit Stream)
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    org_id VARCHAR(64) NOT NULL,
    action VARCHAR(32) NOT NULL,
    patient_id VARCHAR(64),
    record_id VARCHAR(64),
    status VARCHAR(16) DEFAULT 'SUCCESS',
    details TEXT
);

-- 15. Organization Users Table (Organization Login Only - NO PATIENT LOGIN)
CREATE TABLE IF NOT EXISTS users (
    username VARCHAR(32) PRIMARY KEY,
    password_hash CHAR(64) NOT NULL,
    org_id VARCHAR(64) NOT NULL,
    org_name VARCHAR(128) NOT NULL,
    role VARCHAR(32) NOT NULL -- 'HOSPITAL', 'INSURANCE', 'ADMIN'
);

-- High-Performance B-Tree Indexes
CREATE INDEX IF NOT EXISTS idx_encounters_patient ON encounters(patient_id);
CREATE INDEX IF NOT EXISTS idx_encounters_org ON encounters(organization_id);
CREATE INDEX IF NOT EXISTS idx_encounters_block ON encounters(block_index);
CREATE INDEX IF NOT EXISTS idx_conditions_enc ON conditions(encounter_id);
CREATE INDEX IF NOT EXISTS idx_medications_enc ON medications(encounter_id);
CREATE INDEX IF NOT EXISTS idx_procedures_enc ON procedures(encounter_id);
CREATE INDEX IF NOT EXISTS idx_immunizations_enc ON immunizations(encounter_id);
CREATE INDEX IF NOT EXISTS idx_observations_enc ON observations(encounter_id);
CREATE INDEX IF NOT EXISTS idx_claims_enc ON claims(encounter_id);
CREATE INDEX IF NOT EXISTS idx_claims_patient ON claims(patient_id);
CREATE INDEX IF NOT EXISTS idx_tx_record ON blockchain_transactions(record_id);
CREATE INDEX IF NOT EXISTS idx_tx_block ON blockchain_transactions(block_index);
