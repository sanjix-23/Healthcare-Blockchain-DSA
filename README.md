# Blockchain-Based Healthcare Record Integrity and Secure Medical Data Sharing

A functional DSA-based healthcare data integrity prototype using **SHA-256, Merkle Trees, Blockchain, Custom Hash Tables, and Linked Lists**.

---

## 1. Problem Statement

Healthcare organizations such as hospitals, laboratories, and insurance companies exchange large amounts of electronic health record (EHR) and billing information.

In a conventional centralized system, healthcare records are stored in databases where unauthorized modification or accidental alteration may be difficult to detect.

This project presents a **Blockchain-Based Healthcare Record Integrity and Secure Medical Data Sharing** prototype that demonstrates how Data Structures and Algorithms can be used to improve the integrity and verification of healthcare records.

The system combines:

- SHA-256 cryptographic hashing
- Merkle Trees
- Hash-linked Blockchain
- Custom Hash Table
- Linked Lists
- SQLite database
- Role-based demonstration workflows
- Audit logging
- Tamper detection
- Performance benchmarking

The primary purpose of the project is to demonstrate how these DSA and cryptographic techniques can be applied to healthcare data integrity in an educational prototype.

### Example Workflow

```text
Patient visits Hospital A
        |
        v
Hospital A stores EHR
        |
        v
EHR is converted into canonical form
        |
        v
SHA-256 hash generated
        |
        v
Hash becomes Merkle Tree leaf
        |
        v
Merkle Root generated
        |
        v
Merkle Root anchored in Blockchain
        |
        v
Hospital B / Insurance retrieves record
        |
        v
Integrity verification
```

The system does not attempt to replace a production Electronic Health Record system. It is designed as a **college DSA capstone functional prototype** demonstrating data structures, hashing, integrity verification, and blockchain concepts.

---

## 2. Objectives

The main objectives of the project are:

### 2.1 Healthcare Record Integrity

Provide a mechanism for detecting unauthorized modification of healthcare records using cryptographic hashes.

### 2.2 SHA-256 Based Verification

Generate deterministic SHA-256 hashes for canonical healthcare record packages.

### 2.3 Merkle Tree Based Verification

Organize multiple record hashes into a binary Merkle Tree and calculate a Merkle Root for efficient integrity verification.

### 2.4 Blockchain Hash Linking

Store Merkle Roots in a hash-linked blockchain structure where each block references the previous block.

```text
Block N-1
   |
   | previous_hash
   v
Block N
   |
   | previous_hash
   v
Block N+1
```

Modification of an earlier block therefore affects the hash relationship with subsequent blocks.

### 2.5 Secure Medical Data Sharing Demonstration

Demonstrate how healthcare organizations can retrieve and verify patient records across organizational boundaries.

For example:

```text
Hospital A
     |
     v
Healthcare Record System
     |
     v
Hospital B
     |
     v
Retrieve + Verify
```

### 2.6 Data Structure Implementation

Implement important data structures manually rather than relying entirely on built-in data structures.

The project includes:

- Custom Hash Table
- Patient History Linked List
- Audit Log Linked List
- Merkle Tree
- Blockchain

### 2.7 Tamper Detection

Demonstrate how modification of clinical or billing information can be detected through hash and Merkle verification.

### 2.8 Auditability

Maintain an audit trail of important system actions such as authentication and data access.

### 2.9 Performance Measurement

Provide benchmarks for important operations including:

- SHA-256 hashing
- Merkle Tree construction
- Merkle proof generation
- Hash Table lookup
- Linear search comparison
- Blockchain validation

### 2.10 Educational Demonstration

Provide a web-based interface that allows the user to visually demonstrate:

- Patient search
- EHR retrieval
- Integrity verification
- Tamper detection
- Claim verification
- Blockchain exploration
- Merkle Tree visualization
- Data structure operations
- Performance benchmarking

---

## 3. Key Features

### 3.1 Patient Search

Users can search the healthcare database using patient ID or patient name.

Example:

```text
Search:
P001171
```

The system returns the corresponding patient information and available healthcare records.

---

### 3.2 Longitudinal EHR Retrieval

The application can retrieve a patient's longitudinal healthcare record.

The EHR view can contain:

- Patient demographics
- Encounters
- Conditions
- Medications
- Procedures
- Immunizations
- Observations
- Claims
- Record hash
- Blockchain block information
- Merkle leaf information

The patient's encounter history is organized using the custom linked-list implementation.

---

### 3.3 SHA-256 Record Hashing

Each healthcare record package is converted into a deterministic representation and hashed using SHA-256.

Example:

```text
Healthcare Record
       |
       v
Canonical Representation
       |
       v
SHA-256
       |
       v
64-character hexadecimal hash
```

Any modification to the underlying record produces a different hash.

---

### 3.4 Merkle Tree Integrity

Multiple healthcare transaction hashes are organized into a binary Merkle Tree.

For example:

```text
                 Merkle Root
                /           \
             Hash           Hash
            /   \          /   \
         Hash   Hash     Hash   Hash
          |      |        |      |
        Tx 1    Tx 2     Tx 3    Tx 4
```

The application can generate and verify Merkle proofs for individual transactions.

---

### 3.5 Blockchain Ledger

The system maintains an educational hash-linked blockchain.

Each block contains information such as:

- Block index
- Timestamp
- Previous block hash
- Current block hash
- Nonce
- Merkle Root
- Transactions
- Mining organization

Example:

```text
Genesis Block
      |
      v
Block 1
      |
      v
Block 2
      |
      v
Block 3
      |
      v
...
```

---

### 3.6 Custom Hash Table

A custom hash table is implemented using **separate chaining**.

It provides:

- Hash-based key generation
- Collision handling
- Key-value storage
- Dynamic resizing
- Lookup operations

The implementation uses a polynomial rolling hash approach and resizes when the load factor exceeds the configured threshold.

---

### 3.7 Linked Lists

Two linked-list based structures are implemented.

#### Patient History Linked List

Used for organizing a patient's chronological healthcare encounter history.

```text
Head
 |
 v
Encounter 1 -> Encounter 2 -> Encounter 3 -> NULL
```

#### Audit Log Linked List

Used to organize audit events.

```text
Head
 |
 v
Login -> Search -> EHR Access -> Verification -> NULL
```

---

### 3.8 Tamper Demonstration

The application provides controlled tampering demonstrations.

#### Clinical Tampering

A clinical field can be intentionally modified.

The system then detects the mismatch between the current record hash and the previously anchored hash.

#### Billing Tampering

A billing or claim value can be intentionally changed.

The verification system detects the resulting integrity mismatch.

After the demonstration, the record can be restored to its original state.

---

### 3.9 Cross-Hospital Retrieval

The prototype demonstrates the following scenario:

```text
                Healthcare System
                       |
          +------------+------------+
          |                         |
          v                         v
     Hospital A                Hospital B
          |                         |
     Create EHR               Retrieve EHR
          |                         |
          +------------+------------+
                       |
                       v
                  Verification
```

Hospital B can retrieve and verify a patient's existing EHR without requiring the patient to have a separate login.

---

### 3.10 Insurance Claim Verification

The Insurance role can search for claims and verify billing integrity.

The verification process checks:

```text
Claim Data
    |
    v
Record Hash
    |
    v
Merkle Proof
    |
    v
Blockchain Validation
    |
    v
Integrity Status
```

A valid claim produces a verified integrity result.

---

### 3.11 Blockchain Explorer

The application provides a blockchain explorer showing:

- Block index
- Previous hash
- Current hash
- Merkle Root
- Nonce
- Transaction count
- Timestamp
- Block validation status

---

### 3.12 Data Structure Visualizer

The application includes a dedicated Data Structure Visualizer.

It demonstrates the actual blockchain and Merkle Tree data used by the application.

For example, Block #122 contains 500 transactions.

```text
500 Transaction Hashes
        |
        v
500 Merkle Leaves
        |
        v
Binary Merkle Tree
        |
        v
Merkle Root
```

For 500 leaves, the visualizer demonstrates a tree with approximately 10 levels of reduction:

```text
500
 |
250
 |
125
 |
63
 |
32
 |
16
 |
8
 |
4
 |
2
 |
1
```

The visualizer also displays blockchain relationships such as:

```text
Block #122
    |
    v
Block #121
    |
    v
Block #120
```

---

### 3.13 Audit Trail

Important application activities are recorded in an audit log.

Examples include:

- Login
- Patient search
- EHR access
- Integrity verification
- Claim access
- Tamper demonstration
- Restore operation

The Admin interface can inspect these events.

---

### 3.14 Performance Benchmark

The system includes a benchmark section for measuring the performance of important DSA and cryptographic operations.

The benchmark covers:

```text
SHA-256
Merkle Tree
Merkle Proof
Custom Hash Table
Linear Search
Blockchain Validation
```

The results help demonstrate the computational characteristics of the implemented structures and algorithms.
## 4. System Architecture

The system follows a layered architecture combining the web interface, FastAPI backend, SQLite database, custom DSA implementations, cryptographic integrity mechanisms, and blockchain ledger.

### 4.1 High-Level Architecture

```text
+------------------------------------------------------+
|                  Web Frontend                        |
|             HTML + CSS + JavaScript                  |
+---------------------------+--------------------------+
                            |
                            | HTTP / REST API
                            v
+------------------------------------------------------+
|                  FastAPI Backend                     |
|                                                      |
|  Authentication | Patients | Encounters | Claims    |
|  Blockchain     | Audit    | Tamper    | Benchmark  |
+---------------------------+--------------------------+
                            |
             +--------------+--------------+
             |                             |
             v                             v
+--------------------------+    +---------------------+
|       DSA Layer          |    |    SQLite Database  |
|                          |    |                     |
| Custom Hash Table       |    | Patients            |
| Linked Lists            |    | Encounters          |
| Merkle Tree             |    | Conditions          |
| Blockchain              |    | Medications         |
+--------------------------+    | Procedures          |
             |                  | Claims              |
             |                  | Audit Logs          |
             v                  +---------------------+
+------------------------------------------------------+
|             Cryptographic Integrity                  |
|                                                      |
|              SHA-256 Record Hashes                   |
|                       |                              |
|                       v                              |
|                  Merkle Tree                         |
|                       |                              |
|                       v                              |
|                  Merkle Root                         |
|                       |                              |
|                       v                              |
|               Blockchain Block                       |
+------------------------------------------------------+
```

---

### 4.2 Application Layers

The project can be divided into the following logical layers.

#### Presentation Layer

Implemented using:

- HTML
- CSS
- JavaScript

Responsible for:

- Login interface
- Dashboard
- Patient search
- EHR display
- Integrity verification
- Claims
- Blockchain explorer
- Audit trail
- Benchmark results
- Data Structure Visualizer

---

#### API Layer

Implemented using **FastAPI**.

The API layer provides REST endpoints for:

- Authentication
- Patient management
- EHR retrieval
- Encounter creation
- Claim verification
- Blockchain inspection
- Audit retrieval
- Tamper demonstration
- Performance benchmarking

---

#### Data Layer

Implemented using **SQLite**.

The database stores structured healthcare information including:

- Patients
- Organizations
- Providers
- Payers
- Encounters
- Conditions
- Medications
- Procedures
- Immunizations
- Observations
- Claims
- Blockchain metadata
- Audit records
- Users

---

#### DSA and Integrity Layer

This layer contains the project's core algorithmic components:

```text
SHA-256
   |
   v
Merkle Tree
   |
   v
Blockchain

Hash Table
   |
   v
Fast Lookup

Linked Lists
   |
   v
Patient History / Audit Trail
```

---

### 4.3 Merkle Tree

The project implements a binary Merkle Tree for efficient integrity verification.

Each healthcare transaction first produces a SHA-256 hash.

These hashes become the leaves of the Merkle Tree.

For example:

```text
Transaction 1 ──> H1
Transaction 2 ──> H2
Transaction 3 ──> H3
Transaction 4 ──> H4
                    |
                    v

                 H12 = H(H1 + H2)
                 H34 = H(H3 + H4)
                    |
                    v

              Merkle Root
             H(H12 + H34)
```

The implementation uses:

- Binary tree structure
- Pairwise hashing
- Odd-node duplication when required
- Merkle Root calculation
- Merkle proof generation
- Merkle proof verification

#### Merkle Proof

A Merkle proof allows an individual transaction to be verified without reconstructing the entire database.

Conceptually:

```text
Transaction Hash
       |
       +---- Sibling Hash
       |
       v
Parent Hash
       |
       +---- Sibling Hash
       |
       v
...
       |
       v
Merkle Root
```

The computed root is compared with the Merkle Root stored in the blockchain block.

---

### 4.4 SHA-256

SHA-256 is used as the primary cryptographic hashing mechanism in the project.

The process is:

```text
EHR Data
   |
   v
Canonical JSON
   |
   v
SHA-256
   |
   v
Record Hash
```

SHA-256 produces a 256-bit digest represented as a 64-character hexadecimal string.

Example:

```text
c9becbf81d3de28c560c49aa15b67e0d686713cb6346d7f96b16169bf9b584f8
```

The deterministic canonical representation ensures that the same logical record produces the same hash when represented identically.

---

## 5. Cryptographic Integrity Flow

The complete integrity pipeline used by the application is:

```text
                Healthcare Record
                       |
                       v
              Canonical Serialization
                       |
                       v
                    SHA-256
                       |
                       v
                 Record Hash
                       |
                       v
                Merkle Tree Leaf
                       |
                       v
                 Merkle Root
                       |
                       v
                Blockchain Block
                       |
                       v
              Integrity Verification
```

### 5.1 Record Hash Generation

When an encounter is created, the relevant healthcare information is converted into a canonical package.

The package includes information associated with the encounter and its related healthcare data.

The canonical package is then hashed using SHA-256.

---

### 5.2 Merkle Tree Construction

The generated record hash is inserted as a Merkle Tree leaf.

For multiple transactions:

```text
                Merkle Root
               /           \
             H12           H34
            /   \         /   \
          H1    H2       H3    H4
          |     |        |     |
         Tx1   Tx2      Tx3   Tx4
```

The resulting Merkle Root summarizes the integrity of all transactions in the block.

---

### 5.3 Blockchain Anchoring

The Merkle Root is stored in a blockchain block.

Each block also contains:

- Block index
- Timestamp
- Previous block hash
- Merkle Root
- Block hash
- Nonce
- Transaction information

The block hash is calculated from the block contents.

The blockchain therefore provides two levels of integrity:

```text
Transaction Integrity
        |
        v
Merkle Tree
        |
        v
Merkle Root
        |
        v
Block Integrity
        |
        v
Hash-linked Blockchain
```

---

### 5.4 Verification Process

When a record is retrieved, the application performs integrity verification.

```text
Current EHR
    |
    v
Generate Current SHA-256 Hash
    |
    v
Compare with Anchored Record Hash
    |
    +---- Match ------> Hash Valid
    |
    +---- Mismatch ---> Possible Tampering
```

If the record hash matches, the system additionally checks the Merkle proof and blockchain block.

The final verification therefore checks:

```text
SHA-256 Hash
      +
Merkle Proof
      +
Blockchain Validation
      |
      v
Integrity Status
```

A successful verification is displayed as:

```text
SHA-256       MATCH
Merkle Proof  VALID
Blockchain    VALID
--------------------
INTEGRITY     VERIFIED
```

---

## 6. Tamper Detection

The application includes a controlled tamper demonstration to show how blockchain and Merkle-based integrity checking can detect modifications to healthcare records.

### 6.1 Normal State

Initially, the stored EHR matches the cryptographic information anchored in the blockchain.

```text
Database Record
      |
      v
SHA-256 Hash
      |
      v
Stored Record Hash
      |
      v
Merkle Root
      |
      v
Blockchain
```

Result:

```text
SHA-256       MATCH
Merkle Proof  VALID
Blockchain    VALID
Status        VERIFIED
```

---

### 6.2 Clinical Data Tampering

During the demonstration, a clinical field is intentionally modified in the database without modifying the blockchain record.

For example:

```text
Original Clinical Data
        |
        v
Base Cost = 175.50
```

After controlled tampering:

```text
Modified Clinical Data
        |
        v
Base Cost = 99999.00
```

The blockchain still contains the original cryptographic commitment.

Therefore:

```text
Modified EHR
     |
     v
New SHA-256 Hash
     |
     X
Original Anchored Hash
```

The system detects the mismatch.

---

### 6.3 Verification After Tampering

After tampering, the application displays:

```text
SHA-256       MISMATCH
Merkle Proof  INVALID
Blockchain    VALID
--------------------
Status        TAMPER DETECTED
```

The blockchain itself remains structurally valid because the demonstration modifies the off-chain database record rather than rewriting the blockchain.

This demonstrates an important distinction:

> Blockchain validation confirms the integrity of the stored blockchain structure, while record-hash verification detects whether the current healthcare record differs from the originally anchored record.

---

### 6.4 Billing Tampering

The same concept is demonstrated for billing information.

Example:

```text
Original Claim Amount
        |
        v
₹175.50
```

Controlled tampering:

```text
Modified Claim Amount
        |
        v
₹99,999.00
```

The resulting record no longer matches the cryptographic commitment.

The claim verification process can therefore identify the billing integrity failure.

---

### 6.5 Restore Demonstration

After demonstrating tampering, the prototype provides a restore operation that returns the demonstration record to its original state.

After restoration:

```text
Original Record
      |
      v
SHA-256 MATCH
      |
      v
Merkle Proof VALID
      |
      v
Blockchain VALID
      |
      v
INTEGRITY VERIFIED
```

The restore operation is intended only for the controlled educational demonstration.

In a real healthcare system, authorized correction would normally require appropriate versioning, audit trails, access controls, and institutional procedures rather than silently overwriting historical information.

## 7. User Roles

The prototype provides different demonstration roles representing the major organizations involved in healthcare data exchange.

The system uses three main operational roles:

- Hospital
- Insurance
- Admin

Two hospital demo accounts are provided to demonstrate cross-hospital record sharing.

### 7.1 Hospital Role

The Hospital role represents a healthcare organization that creates and retrieves patient records.

Hospital users can:

- Search patients
- View patient profiles
- Retrieve EHRs
- View medical encounters
- View clinical information
- Verify record integrity
- Demonstrate controlled clinical tampering
- Restore the demonstration record

The system includes two hospital accounts:

```text
Hospital A
Hospital B
```

This allows the project to demonstrate:

```text
Hospital A
    |
    | Creates / stores record
    v
Healthcare Record
    |
    | Retrieve
    v
Hospital B
    |
    | Verify
    v
Integrity Result
```

---

### 7.2 Insurance Role

The Insurance role represents an insurance organization that needs to inspect and verify billing information.

Insurance users can:

- Search claims
- View claim details
- Verify claim integrity
- Check billing information
- Verify SHA-256 hash
- Verify Merkle proof
- Verify blockchain integrity

The Insurance role is intended as a read-oriented demonstration workflow.

---

### 7.3 Admin Role

The Admin role provides access to system-level functionality.

Admin users can access:

- Blockchain Explorer
- Audit Trail
- Performance Benchmark
- Data Structure Visualizer
- Claims
- Integrity verification
- Controlled tamper demonstrations

The Admin role is intended for demonstrating the internal working of the DSA and blockchain components.

---

### 7.4 No Patient Login

The prototype intentionally does **not** require a separate patient login.

The demonstration workflow assumes that authorized healthcare organizations retrieve a patient's record through the healthcare system.

For example:

```text
Patient
   |
   v
Hospital A
   |
   v
Stores EHR
   |
   v
Hospital B / Insurance
   |
   v
Retrieves and verifies record
```

This design keeps the prototype focused on the project's primary DSA objective: **healthcare record integrity and verification**.

---

## 8. Demo Accounts

The project contains predefined demonstration accounts for testing the different workflows.

### 8.1 Hospital A

```text
Username: hospital_a
Password: hospital_a_pass
Role: HOSPITAL
Organization: LAHEY HOSPITAL & MEDICAL CENTER BURLINGTON
```

Hospital A can be used to demonstrate:

- Patient search
- EHR retrieval
- Integrity verification
- Clinical tamper detection
- Record restoration

---

### 8.2 Hospital B

```text
Username: hospital_b
Password: hospital_b_pass
Role: HOSPITAL
Organization: BETH ISRAEL DEACONESS HOSPITAL
```

Hospital B can be used to demonstrate:

- Cross-hospital patient retrieval
- EHR access
- Record integrity verification

---

### 8.3 Insurance

```text
Username: insurance_bcbs
Password: insurance_pass
Role: INSURANCE
Organization: BLUE CROSS BLUE SHIELD
```

The Insurance account can be used to demonstrate:

- Claim search
- Claim retrieval
- Billing verification
- Merkle proof verification
- Blockchain verification

---

### 8.4 Admin

```text
Username: admin
Password: admin_pass
Role: ADMIN
```

The Admin account can be used to demonstrate:

- Blockchain Explorer
- Audit Trail
- Performance Benchmark
- Data Structure Visualizer
- Claims
- Tamper demonstrations

---

### 8.5 Authentication Flow

The login process is:

```text
Username + Password
        |
        v
Authentication API
        |
        v
Password Hash Verification
        |
        v
Role Identification
        |
        v
Role-specific Dashboard
```

Login activities are also recorded in the audit trail.

---

## 9. Recommended Demonstration Flow

The following sequence demonstrates the major features of the project in a logical order.

### Stage 1 — Hospital A: EHR and Integrity

Login using:

```text
hospital_a
hospital_a_pass
```

Then:

1. Search for patient `P001171`.
2. Open the patient EHR.
3. Display the medical encounter.
4. Show the SHA-256 record hash.
5. Show the blockchain block information.
6. Run integrity verification.
7. Demonstrate clinical tampering.
8. Run verification again.
9. Show the tamper detection result.
10. Restore the record.
11. Verify again.

Expected final result:

```text
SHA-256       MATCH
Merkle Proof  VALID
Blockchain    VALID
Status        VERIFIED
```

---

### Stage 2 — Hospital B: Cross-Hospital Verification

Logout and login using:

```text
hospital_b
hospital_b_pass
```

Then:

1. Search for `P001171`.
2. Open the patient's EHR.
3. Display the record originally stored by Hospital A.
4. Run integrity verification.

This demonstrates cross-hospital retrieval and verification.

Conceptually:

```text
Hospital A
    |
    | EHR
    v
Healthcare System
    |
    | Retrieve
    v
Hospital B
    |
    v
Verify Integrity
```

---

### Stage 3 — Insurance: Claim Verification

Logout and login using:

```text
insurance_bcbs
insurance_pass
```

Then:

1. Open the Claims section.
2. Search for patient `P001171`.
3. Select the available claim.
4. Display claim details.
5. Run billing integrity verification.

Expected result:

```text
Billing Integrity: VERIFIED
SHA-256: MATCH
Merkle Proof: VALID
Blockchain: VALID
```

---

### Stage 4 — Admin: Blockchain and Audit

Login using:

```text
admin
admin_pass
```

Open the Admin sections and demonstrate:

- Blockchain Explorer
- Block details
- Blockchain validation
- Audit Trail
- Performance Benchmark

Show that the blockchain ledger is currently valid.

---

### Stage 5 — DSA Visualizer

Open the **Data Structure Visualizer**.

The recommended demonstration block is:

```text
Block #122
```

The visualizer can demonstrate:

```text
500 Transactions
       |
       v
500 Merkle Leaves
       |
       v
Merkle Tree
       |
       v
Merkle Root
       |
       v
Blockchain Block #122
       |
       v
Previous Block #121
```

The visualizer displays:

- Selected block
- Transaction count
- Tree height
- Merkle Root
- Calculated Root
- Merkle verification status
- Blockchain links

This section is particularly useful for explaining where the project's DSA concepts are implemented.

---

### 9.1 Suggested 5-Minute Presentation Sequence

For a short faculty demonstration, the following sequence can be used:

```text
0:00 - 0:30
Project introduction

0:30 - 1:15
Hospital A → Patient Search → EHR

1:15 - 2:00
SHA-256 + Merkle + Blockchain Verification

2:00 - 2:45
Clinical Tampering → Detection → Restore

2:45 - 3:30
Hospital B → Cross-Hospital Retrieval

3:30 - 4:00
Insurance → Claim Verification

4:00 - 4:40
Admin → Blockchain + Audit

4:40 - 5:00
DSA Visualizer → Merkle Tree + Blockchain
```

The presentation should focus on the relationship between the implemented data structures and the healthcare integrity workflow rather than spending excessive time navigating the interface.

## 10. Technology Stack

The project uses a lightweight technology stack so that the DSA implementations remain clearly visible and easy to demonstrate.

### 10.1 Programming Language

**Python**

Python is used for:

- Backend development
- DSA implementations
- Cryptographic operations
- Database operations
- Blockchain implementation
- Benchmarking
- Testing

---

### 10.2 Backend Framework

**FastAPI**

FastAPI provides the REST API layer between the frontend and the healthcare data and integrity components.

Major API areas include:

```text
Authentication
Patients
Encounters
Claims
Blockchain
Audit
Tamper Detection
Performance Benchmark
```

---

### 10.3 Database

**SQLite**

SQLite is used as the local relational database.

The database stores structured healthcare information and system metadata.

Major tables include:

```text
patients
organizations
providers
payers
encounters
conditions
medications
procedures
immunizations
observations
claims
blockchain_blocks
blockchain_transactions
audit_log
users
```

SQLite was selected for the educational prototype because it provides a lightweight relational database without requiring a separate database server.

---

### 10.4 Frontend

The frontend uses:

- HTML5
- CSS3
- Vanilla JavaScript

No React, Angular, Vue, or npm-based frontend framework is required.

This keeps the application simple and makes the DSA implementation independent of a frontend framework.

---

### 10.5 Cryptography

The project uses:

**SHA-256**

SHA-256 is used for:

- Healthcare record hashing
- Password hashing for demo authentication
- Blockchain block hashing
- Integrity verification

The browser-side Data Structure Visualizer also uses the browser's Web Crypto API for cryptographic visualization where required.

---

### 10.6 Data Structures and Algorithms

The project implements the following major DSA components:

| Data Structure / Algorithm | Purpose |
|---|---|
| SHA-256 | Cryptographic integrity |
| Merkle Tree | Efficient multi-record verification |
| Blockchain | Hash-linked integrity ledger |
| Custom Hash Table | Fast key-based lookup |
| Singly Linked List | Patient history |
| Linked List | Audit log |
| Binary Tree | Merkle Tree structure |
| Proof of Work | Educational blockchain mining |
| Linear Search | Benchmark comparison |
| Hash-based Lookup | Performance comparison |

---

### 10.7 Testing

The project uses:

**pytest**

Automated tests cover the core DSA components and database/blockchain integration.

The project includes separate testing for:

- Phase 1 DSA components
- Phase 2 database and blockchain integration
- Backend/API functionality

---

### 10.8 Data Source

The project uses **Synthea synthetic healthcare data**.

Synthea provides synthetic patient records suitable for educational and development purposes.

The imported dataset contains healthcare information such as:

- Patients
- Encounters
- Conditions
- Medications
- Procedures
- Immunizations
- Observations
- Claims

Sensitive fields such as exact street addresses and other direct sensitive identifiers were excluded from the imported project dataset.

---

## 11. Project Structure

The project is organized into separate layers for DSA implementation, database management, backend APIs, frontend interface, scripts, and tests.

```text
Healthcare-Blockchain-DSA/
│
├── backend/
│   ├── __init__.py
│   ├── app.py
│   ├── models.py
│   ├── state.py
│   │
│   └── routes/
│       ├── __init__.py
│       ├── audit.py
│       ├── auth.py
│       ├── benchmark.py
│       ├── blockchain.py
│       ├── claims.py
│       ├── encounters.py
│       ├── patients.py
│       └── tamper.py
│
├── blockchain_data/
│   └── healthcare_ehr.db
│
├── core/
│   ├── __init__.py
│   ├── blockchain.py
│   ├── crypto.py
│   ├── hash_table.py
│   ├── linked_list.py
│   └── merkle_tree.py
│
├── db/
│   ├── database.py
│   └── schema.sql
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── scripts/
│   └── import_synthea.py
│
├── tests/
│   ├── test_phase1.py
│   └── test_phase2_db_blockchain.py
│
├── dataset/
│   └── Synthea dataset files
│
├── .gitattributes
├── .gitignore
├── requirements.txt
└── README.md
```

### 11.1 Core Directory

The `core/` directory contains the primary DSA and cryptographic implementations.

#### `core/crypto.py`

Contains:

- SHA-256 wrapper
- Canonical JSON serialization
- EHR package hashing

#### `core/merkle_tree.py`

Contains:

- Merkle Tree construction
- Merkle Root generation
- Merkle proof generation
- Merkle proof verification

#### `core/blockchain.py`

Contains:

- Block structure
- Blockchain structure
- Previous-hash linking
- Block hashing
- Proof of Work
- Blockchain validation

#### `core/hash_table.py`

Contains the custom hash table implementation using separate chaining.

#### `core/linked_list.py`

Contains linked-list implementations for:

- Patient history
- Audit logging

---

### 11.2 Database Directory

The `db/` directory contains database-related functionality.

#### `db/schema.sql`

Defines the relational database schema.

#### `db/database.py`

Provides:

- SQLite connection handling
- Schema initialization
- Database operations
- Audit support
- Canonical encounter package generation

---

### 11.3 Backend Directory

The `backend/` directory contains the FastAPI application.

`backend/app.py` initializes the FastAPI application and registers the API routes.

The `routes/` directory separates API functionality into logical modules.

---

### 11.4 Frontend Directory

The `frontend/` directory contains the complete browser interface.

```text
index.html
    |
    +---- Page structure

style.css
    |
    +---- Visual design

app.js
    |
    +---- API communication
    +---- UI logic
    +---- Integrity visualization
    +---- Data Structure Visualizer
```

---

### 11.5 Scripts Directory

The `scripts/` directory contains utility scripts.

The primary script is:

```text
import_synthea.py
```

It is responsible for importing Synthea data into the database and creating the corresponding blockchain records.

**Important:** The database supplied with the project is already populated. A normal demonstration does not require running the import script again.

---

### 11.6 Tests Directory

The `tests/` directory contains automated tests for the project.

The tests verify the functionality of the DSA components and database/blockchain integration.

---

## 12. Installation and Setup

### 12.1 Prerequisites

The following software is required:

- Python 3.x
- Git
- Git LFS
- A modern web browser

The project has been developed and tested on Windows.

---

### 12.2 Clone the Repository

Clone the project from GitHub:

```bash
git clone https://github.com/sanjix-23/Healthcare-Blockchain-DSA.git
```

Move into the project directory:

```bash
cd Healthcare-Blockchain-DSA
```

---

### 12.3 Git LFS

The healthcare SQLite database is stored using **Git Large File Storage (Git LFS)** because of its size.

Install Git LFS if it is not already installed.

Then initialize it:

```bash
git lfs install
```

If the repository was cloned before Git LFS was initialized, run:

```bash
git lfs pull
```

Verify the database file:

```text
blockchain_data/healthcare_ehr.db
```

The repository uses Git LFS for this database file.

The raw Synthea dataset is not included in the GitHub repository because of its large size.

---

### 12.4 Create a Python Virtual Environment

From the project root:

```bash
python -m venv .venv
```

Activate the virtual environment on Windows:

```bash
.venv\Scripts\activate
```

After activation, the terminal should show something similar to:

```text
(.venv) C:\Healthcare-Blockchain-DSA>
```

---

### 12.5 Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

The main backend dependencies are:

```text
fastapi
pydantic
uvicorn
```

The remaining project functionality primarily uses Python's standard library and the project's own modules.

## 13. Running the Application

The project consists of two components that need to run simultaneously:

```text
Frontend
   |
   | HTTP Requests
   v
FastAPI Backend
   |
   v
SQLite + DSA + Blockchain
```

The backend provides the REST API, while the frontend provides the browser-based interface.

---

### 13.1 Start the Backend

Open a terminal in the project root:

```bash
cd C:\Healthcare-Blockchain-DSA
```

Activate the virtual environment:

```bash
.venv\Scripts\activate
```

Start the FastAPI server:

```bash
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload
```

The backend should start at:

```text
http://127.0.0.1:8000
```

A successful startup displays output similar to:

```text
Uvicorn running on http://127.0.0.1:8000
Application startup complete.
```

---

### 13.2 Backend API Documentation

FastAPI automatically provides interactive API documentation.

Open:

```text
http://127.0.0.1:8000/docs
```

The Swagger interface can be used to:

- View API endpoints
- Inspect request models
- Send test requests
- Inspect JSON responses
- Verify backend functionality

An alternative ReDoc interface is available at:

```text
http://127.0.0.1:8000/redoc
```

---

### 13.3 Start the Frontend

Open a second terminal.

Move to the project root:

```bash
cd C:\Healthcare-Blockchain-DSA
```

Start the Python HTTP server:

```bash
python -m http.server 5500 --directory frontend
```

The frontend will be available at:

```text
http://127.0.0.1:5500
```

Open this address in a browser.

---

### 13.4 Running Both Components

The final setup should have two terminals.

#### Terminal 1 — Backend

```bash
cd C:\Healthcare-Blockchain-DSA
.venv\Scripts\activate
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload
```

#### Terminal 2 — Frontend

```bash
cd C:\Healthcare-Blockchain-DSA
python -m http.server 5500 --directory frontend
```

Then open:

```text
http://127.0.0.1:5500
```

---

### 13.5 Backend Health Check

The root API endpoint can be opened at:

```text
http://127.0.0.1:8000/
```

It provides basic project and backend status information.

The API also exposes the current:

- Application status
- Number of indexed patients
- Blockchain height
- Supported roles

---

## 14. API Endpoints

The backend exposes REST APIs organized by functionality.

### 14.1 Authentication

```text
POST /api/auth/login
```

Used for demonstration login.

Example roles:

```text
HOSPITAL
INSURANCE
ADMIN
```

---

```text
GET /api/auth/demo-accounts
```

Returns the available demonstration account information.

---

### 14.2 Patient APIs

```text
GET /api/patients/search
```

Search patients by ID or name.

Example:

```text
GET /api/patients/search?q=P001171
```

---

```text
GET /api/patients/{patient_id}
```

Returns basic patient information.

---

```text
GET /api/patients/{patient_id}/ehr
```

Returns the patient's longitudinal EHR.

The endpoint can include:

- Patient information
- Encounters
- Conditions
- Medications
- Procedures
- Immunizations
- Observations
- Claims
- Record hashes
- Blockchain references
- Merkle leaf information

---

```text
POST /api/patients
```

Creates a new patient record.

---

### 14.3 Encounter APIs

```text
POST /api/encounters
```

Creates a new healthcare encounter and anchors its integrity information.

The processing pipeline is:

```text
Encounter
   |
   v
SQLite
   |
   v
Canonical Package
   |
   v
SHA-256
   |
   v
Merkle Tree
   |
   v
Blockchain
```

---

```text
GET /api/encounters/{encounter_id}/verify
```

Verifies the integrity of a healthcare encounter.

The verification checks:

- Current record hash
- Stored record hash
- Merkle proof
- Blockchain block

---

### 14.4 Claims APIs

```text
GET /api/claims/search
```

Search claims using parameters such as:

```text
patient_id
claim_id
payer_id
limit
```

---

```text
GET /api/claims/{claim_id}
```

Returns claim details.

---

```text
GET /api/claims/{claim_id}/verify
```

Verifies billing and claim integrity.

The verification includes:

```text
Claim Hash
    +
Merkle Proof
    +
Blockchain Validation
```

---

### 14.5 Blockchain APIs

```text
GET /api/blockchain/summary
```

Returns blockchain summary information.

---

```text
GET /api/blockchain/blocks
```

Returns blockchain block information.

---

```text
GET /api/blockchain/blocks/{block_index}
```

Returns details for a specific block.

---

```text
GET /api/blockchain/validate
```

Validates the blockchain.

The validation checks:

- Block hashes
- Previous-hash relationships
- Proof-of-Work requirement
- Merkle Roots

---

### 14.6 Tamper APIs

```text
POST /api/tamper/clinical
```

Performs the controlled clinical tamper demonstration.

---

```text
POST /api/tamper/billing
```

Performs the controlled billing tamper demonstration.

---

```text
POST /api/tamper/restore
```

Restores the demonstration record to its original state.

---

### 14.7 Audit API

```text
GET /api/audit
```

Retrieves audit events.

Optional filters include:

```text
limit
org_id
action
```

The backend uses the custom audit linked-list implementation when processing the audit history.

---

### 14.8 Benchmark API

```text
GET /api/performance/benchmark
```

Runs the project's performance benchmarks.

The benchmark covers operations such as:

- SHA-256
- Merkle Tree construction
- Merkle proof
- Custom Hash Table lookup
- Linear search
- Blockchain validation

---

## 15. Database and Data Model

The application uses SQLite for persistent storage.

The database file is:

```text
blockchain_data/healthcare_ehr.db
```

The schema is defined in:

```text
db/schema.sql
```

---

### 15.1 Patient Data

The `patients` table stores basic patient information.

Representative fields include:

```text
patient_id
first_name
last_name
birthdate
gender
race
ethnicity
city
state
zip
```

Sensitive source fields that were not required for the prototype were excluded during Synthea import.

---

### 15.2 Organization Data

Organizations represent healthcare institutions participating in the demonstration.

Examples include:

```text
Hospital A
Hospital B
Insurance Organization
```

Organizations are associated with encounters and other healthcare operations.

---

### 15.3 Provider Data

The provider information represents healthcare professionals associated with encounters.

A healthcare encounter can therefore be associated with:

```text
Patient
   |
   v
Organization
   |
   v
Provider
   |
   v
Encounter
```

---

### 15.4 Payer Data

Payer information is associated with healthcare claims.

The relationship can be represented as:

```text
Patient
   |
   v
Encounter
   |
   v
Claim
   |
   v
Payer
```

This allows the Insurance workflow to retrieve and verify billing information.

---

### 15.5 Encounter Data

An encounter represents a healthcare interaction.

Representative information includes:

```text
Encounter ID
Patient ID
Organization ID
Provider ID
Encounter Class
Description
Start Time
Stop Time
Base Cost
```

An encounter may also have related:

- Conditions
- Medications
- Procedures
- Immunizations
- Observations
- Claims

---

### 15.6 Clinical Data

The database separates several types of clinical information into their own tables.

```text
Encounter
   |
   +---- Conditions
   |
   +---- Medications
   |
   +---- Procedures
   |
   +---- Immunizations
   |
   +---- Observations
```

This normalized structure avoids storing the entire EHR as one large unstructured database field.

---

### 15.7 Claims Data

Claims store billing-related information associated with healthcare encounters.

Representative information includes:

```text
Claim ID
Patient ID
Encounter ID
Payer ID
Status
Total Claim Cost
Payer Coverage
Diagnosis Code
Procedure Code
```

The claim data is used by the Insurance workflow.

---

### 15.8 Blockchain Data

Blockchain information is persisted in dedicated database tables.

The main blockchain information includes:

```text
Block Index
Timestamp
Previous Hash
Merkle Root
Block Hash
Nonce
Transaction Count
Mining Organization
```

Blockchain transactions contain references to the healthcare records whose hashes were anchored into the block.

---

### 15.9 Audit Data

The audit table records important system actions.

Examples include:

```text
Login
Patient Search
EHR Access
Verification
Claim Access
Tamper Operation
Restore Operation
```

The audit information provides a chronological activity history for the prototype.

---

### 15.10 User Data

The users table stores the demonstration authentication information.

The system supports:

```text
HOSPITAL
INSURANCE
ADMIN
```

Passwords are stored using SHA-256 hashes rather than plaintext passwords in the database.

---

### 15.11 Database-to-Blockchain Relationship

The database stores the healthcare record, while the blockchain stores the cryptographic integrity information.

Conceptually:

```text
SQLite Database
      |
      | Healthcare Record
      v
Canonical Record Package
      |
      v
SHA-256 Record Hash
      |
      v
Merkle Tree
      |
      v
Merkle Root
      |
      v
Blockchain
```

The blockchain therefore does not need to contain the complete healthcare record.

Instead, it stores cryptographic information that can be used to verify whether the current record matches the originally anchored record.

## 16. Data Structures and Algorithms Used

A major objective of this project is to demonstrate how Data Structures and Algorithms are applied to a practical healthcare integrity problem.

The major DSA components are:

```text
                    Healthcare System
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
      Hash Table       Linked Lists      Merkle Tree
          |                |                |
          v                v                v
       Lookup        History / Audit    Integrity
                           |
                           v
                       Blockchain
```

---

### 16.1 Custom Hash Table

The project implements a custom hash table using **separate chaining**.

The hash table is useful for key-based lookup operations.

Conceptually:

```text
Key
 |
 v
Hash Function
 |
 v
Bucket Index
 |
 +-------> Linked List of Entries
```

If multiple keys map to the same bucket, separate chaining is used to handle the collision.

Example:

```text
Bucket 0  -> Entry
Bucket 1  -> Entry -> Entry
Bucket 2  -> Entry
Bucket 3  -> NULL
```

The implementation also supports dynamic resizing when the load factor exceeds the configured threshold.

---

### 16.2 Hash Function

The custom hash table uses a polynomial rolling hash approach.

Conceptually:

```text
h(s) = (((c1 × p + c2) × p + c3) × p + ...)
```

The resulting hash value is mapped to a bucket using the table capacity.

The purpose is to distribute keys across the available buckets and reduce collisions.

---

### 16.3 Hash Table Complexity

For a well-distributed hash table:

| Operation | Average Case |
|---|---:|
| Insert | O(1) |
| Search | O(1) |
| Delete | O(1) |

In the worst case, if many keys collide into the same bucket:

```text
Search = O(n)
```

where `n` is the number of entries in the affected chain.

Dynamic resizing helps maintain efficient average performance.

---

### 16.4 Patient History Linked List

The Patient History Linked List organizes encounters associated with a patient.

Example:

```text
HEAD
 |
 v
Encounter 1
 |
 v
Encounter 2
 |
 v
Encounter 3
 |
 v
NULL
```

Each node represents an encounter or history item.

The linked-list representation makes it possible to traverse the patient's chronological history sequentially.

---

### 16.5 Linked List Complexity

For a singly linked list:

| Operation | Complexity |
|---|---:|
| Traverse | O(n) |
| Search | O(n) |
| Insert at head | O(1) |
| Delete known node | O(1) |
| Search + delete | O(n) |

The actual complexity depends on where the operation occurs and whether the target node is already known.

---

### 16.6 Audit Log Linked List

The project also uses a linked-list structure for audit events.

Example:

```text
LOGIN
  |
  v
PATIENT_SEARCH
  |
  v
EHR_ACCESS
  |
  v
VERIFICATION
  |
  v
LOGOUT
```

This provides an ordered representation of system activity.

---

### 16.7 Merkle Tree

The Merkle Tree is a binary tree where leaf nodes represent transaction hashes and internal nodes represent hashes of child nodes.

Example:

```text
                 Root
                /    \
              H12    H34
             /  \    /  \
           H1   H2  H3   H4
```

Each internal node is calculated using the hashes below it.

For example:

```text
H12 = SHA256(H1 + H2)
H34 = SHA256(H3 + H4)

Root = SHA256(H12 + H34)
```

The final root represents the cryptographic summary of all leaves.

---

### 16.8 Merkle Tree Complexity

For `n` leaves:

| Operation | Complexity |
|---|---:|
| Tree Construction | O(n) |
| Root Calculation | O(n) |
| Proof Generation | O(log n) |
| Proof Verification | O(log n) |

This makes Merkle proofs more efficient than processing every transaction when verifying a single transaction.

---

### 16.9 Blockchain

The project implements an educational hash-linked blockchain.

Each block contains:

```text
Block Index
Timestamp
Previous Hash
Merkle Root
Block Hash
Nonce
Transactions
Mining Organization
```

Example:

```text
+----------------------+
| Block #120           |
| Hash: H120           |
+----------+-----------+
           |
           | previous_hash
           v
+----------------------+
| Block #121           |
| Hash: H121           |
+----------+-----------+
           |
           | previous_hash
           v
+----------------------+
| Block #122           |
| Hash: H122           |
+----------------------+
```

---

### 16.10 Blockchain Validation

Blockchain validation checks whether:

1. The block hash is correct.
2. The previous hash reference is correct.
3. The Proof-of-Work requirement is satisfied.
4. The Merkle Root is valid.

Conceptually:

```text
Block Hash
    |
    v
Valid?
    |
    +---- No ----> Invalid Blockchain
    |
   Yes
    |
    v
Previous Hash Valid?
    |
    +---- No ----> Invalid Blockchain
    |
   Yes
    |
    v
Merkle Root Valid?
    |
    +---- No ----> Invalid Block
    |
   Yes
    |
    v
Blockchain Valid
```

---

### 16.11 Proof of Work

The educational blockchain uses a small Proof-of-Work difficulty requirement.

The implementation searches for a nonce that produces a block hash satisfying the configured difficulty.

For the current implementation, the required prefix is:

```text
00
```

Example valid block hash:

```text
00777a467cc96ac2930ae385d45f394dd6d514133ae43e1eb0933aea2944670f
```

The Proof-of-Work mechanism is included to demonstrate the computational concept of blockchain mining.

---

### 16.12 Canonical Data Representation

Before hashing a healthcare record, the data must have a deterministic representation.

The project therefore uses canonical serialization so that logically identical data produces a consistent hash.

The process is:

```text
Healthcare Data
      |
      v
Canonical JSON
      |
      v
SHA-256
      |
      v
Deterministic Hash
```

Without deterministic serialization, differences in formatting or field ordering could produce different hashes even when the underlying information is logically equivalent.

---

## 17. Complexity Analysis

The following table summarizes the major operations implemented in the project.

| Operation | Average Complexity | Worst Case |
|---|---:|---:|
| SHA-256 hashing | O(n) | O(n) |
| Hash Table lookup | O(1) | O(n) |
| Hash Table insertion | O(1) | O(n) |
| Linked List traversal | O(n) | O(n) |
| Linked List search | O(n) | O(n) |
| Merkle Tree construction | O(n) | O(n) |
| Merkle Proof generation | O(log n) | O(log n) |
| Merkle Proof verification | O(log n) | O(log n) |
| Blockchain validation | O(B + T) | O(B + T) |

Where:

- `n` = number of relevant data elements
- `B` = number of blockchain blocks
- `T` = number of transactions being validated

---

### 17.1 SHA-256 Complexity

SHA-256 processes the input data in blocks.

For an input of size `n`:

```text
Time Complexity = O(n)
```

The hash output size remains fixed at 256 bits.

---

### 17.2 Hash Table Complexity

With a well-distributed hash function:

```text
Average Search = O(1)
Average Insert = O(1)
```

With severe collision concentration:

```text
Worst-case Search = O(n)
```

Dynamic resizing is used to control the load factor.

---

### 17.3 Linked List Complexity

Searching a linked list requires sequential traversal.

Therefore:

```text
Search = O(n)
```

Insertion at the head can be performed in:

```text
O(1)
```

This demonstrates the trade-off between simple sequential structures and hash-based lookup.

---

### 17.4 Merkle Tree Complexity

If there are `n` transaction hashes:

```text
Tree Construction = O(n)
```

A Merkle proof only needs the sibling hashes along the path from the leaf to the root:

```text
Proof Size = O(log n)
Verification = O(log n)
```

This is one of the important algorithmic advantages demonstrated by the project.

---

### 17.5 Blockchain Validation Complexity

Blockchain validation requires checking the blocks and their relationships.

If there are `B` blocks and `T` transactions that need to be validated:

```text
Validation ≈ O(B + T)
```

The exact runtime depends on the number of blocks, transactions, and Merkle verification work involved.

---

### 17.6 Space Complexity

The approximate space requirements are:

| Structure | Space Complexity |
|---|---:|
| Hash Table | O(n) |
| Linked List | O(n) |
| Merkle Tree | O(n) |
| Blockchain | O(B + T) |
| SHA-256 output | O(1) |

The healthcare database itself is persistent storage and is separate from the theoretical auxiliary-space analysis of the algorithms.

---

## 18. Sample Dataset and Demonstration State

The project uses **Synthea synthetic healthcare data** as its primary dataset.

Synthea generates synthetic patient histories that can be used for software development and educational demonstrations without using real patient records.

### 18.1 Imported Healthcare Data

The project initially imported thousands of healthcare records across multiple categories, including:

- Patients
- Encounters
- Conditions
- Medications
- Procedures
- Immunizations
- Observations
- Claims

The database was subsequently extended with a dynamic demonstration patient and encounter used for the final integrity and cross-organization workflow.

---

### 18.2 Demonstration Patient

The main demonstration patient is:

```text
Patient ID: P001171
First Name: DynamicEncounter
Last Name: Patient
Birthdate: 1988-11-03
Gender: M
Location: Cambridge, Massachusetts
```

This patient was used for demonstrating:

- Hospital A record creation
- EHR retrieval
- SHA-256 verification
- Merkle verification
- Blockchain anchoring
- Clinical tampering
- Restore
- Hospital B retrieval
- Insurance claim verification

---

### 18.3 Demonstration Encounter

The main demonstration encounter contains:

```text
Description:
Acute Bronchitis Evaluation
```

The encounter includes example clinical information such as:

```text
Condition:
Acute bronchitis (disorder)

Medication:
Acetaminophen 325 MG Oral Tablet

Observation:
Systolic Blood Pressure = 120 mm[Hg]
```

The encounter also contains billing information.

---

### 18.4 Demonstration Blockchain Record

The demonstration encounter is anchored in:

```text
Block #126
```

The block contains one transaction.

Important values include:

```text
Block Index:
126

Transaction Count:
1

Mining Organization:
LAHEY HOSPITAL & MEDICAL CENTER BURLINGTON

Merkle Root:
c9becbf81d3de28c560c49aa15b67e0d686713cb6346d7f96b16169bf9b584f8

Nonce:
31
```

The record hash and Merkle Root correspond to the anchored healthcare encounter.

---

### 18.5 Merkle Visualization Block

For visual demonstration of the Merkle Tree, the project uses:

```text
Block #122
```

This block contains:

```text
Transactions: 500
Tree Height: 10
```

The Data Structure Visualizer displays the actual transaction hashes and constructs the corresponding Merkle Tree.

The calculated Merkle Root is compared with the Merkle Root stored in the blockchain block.

---

### 18.6 Final Demonstration State

The tested prototype state contains approximately:

```text
Patients Indexed: 1171
Blockchain Blocks: 127
Transactions: 61,462
Ledger Status: VALID
```

These values describe the tested local demonstration database and may change if additional records are created.

---

### 18.7 Dataset Privacy

The project uses synthetic data rather than real patient records.

During import, fields that were not necessary for the prototype, including highly sensitive direct identifiers and exact location information, were excluded.

The purpose is to demonstrate healthcare data structures and integrity mechanisms without depending on real patient information.

## 19. Testing and Validation

The project was tested in multiple stages to verify both the individual DSA components and the complete healthcare workflow.

Testing was divided into:

```text
Phase 1
DSA Core Testing
      |
      v
Phase 2
Database + Blockchain Testing
      |
      v
Phase 3
Backend/API Testing
      |
      v
Frontend Functional Testing
      |
      v
End-to-End Demonstration
```

---

### 19.1 Phase 1 — DSA Core Testing

The first phase tested the core implementations independently.

The test suite covers:

- SHA-256 hashing
- Canonical serialization
- Merkle Tree construction
- Merkle Root generation
- Merkle proof generation
- Merkle proof verification
- Blockchain creation
- Blockchain validation
- Hash Table operations
- Linked List operations

The Phase 1 test suite contains:

```text
11 tests
```

The purpose of this phase was to verify that the fundamental data structures and algorithms behaved correctly before integrating them with the healthcare database.

---

### 19.2 Phase 2 — Database and Blockchain Testing

The second phase tested the integration between the SQLite database and the integrity layer.

The tests covered:

- Database initialization
- Healthcare record insertion
- Record hashing
- Merkle Tree generation
- Blockchain anchoring
- Blockchain persistence
- Record retrieval
- Integrity verification

The Phase 2 integration test suite contains:

```text
10 tests
```

---

### 19.3 Backend API Testing

The FastAPI backend was tested through both the frontend application and Swagger API documentation.

Important endpoints tested include:

```text
/api/auth/login
/api/patients/search
/api/patients/{patient_id}/ehr
/api/encounters/{encounter_id}/verify
/api/claims/search
/api/claims/{claim_id}/verify
/api/blockchain/summary
/api/blockchain/validate
/api/audit
/api/performance/benchmark
```

The APIs were also tested for successful JSON responses and expected HTTP status codes.

---

### 19.4 Hospital A Workflow Testing

The Hospital A workflow was tested from login through integrity verification.

The sequence was:

```text
Hospital A Login
       |
       v
Patient Search
       |
       v
EHR Retrieval
       |
       v
Integrity Verification
       |
       v
Clinical Tamper
       |
       v
Tamper Detection
       |
       v
Restore
       |
       v
Verification Again
```

The workflow completed successfully.

---

### 19.5 Clinical Tamper Test

Before tampering:

```text
SHA-256       MATCH
Merkle Proof  VALID
Blockchain    VALID
```

After controlled clinical modification:

```text
SHA-256       MISMATCH
Merkle Proof  INVALID
Blockchain    VALID
Status        TAMPER DETECTED
```

After restoration:

```text
SHA-256       MATCH
Merkle Proof  VALID
Blockchain    VALID
Status        VERIFIED
```

This demonstrates that the system can detect modification of off-chain clinical data.

---

### 19.6 Hospital B Workflow Testing

The Hospital B workflow was tested using the same demonstration patient.

Hospital B successfully:

1. Logged into the system.
2. Searched for the patient.
3. Retrieved the patient's EHR.
4. Viewed the Hospital A encounter.
5. Verified the integrity of the retrieved record.

This demonstrates the cross-hospital retrieval scenario.

---

### 19.7 Insurance Workflow Testing

The Insurance workflow was tested using the demonstration claim.

The claim was successfully:

1. Searched.
2. Retrieved.
3. Verified.

The verification result was:

```text
Billing Integrity: VERIFIED
Hash Match: TRUE
Merkle Proof: TRUE
Blockchain Valid: TRUE
```

---

### 19.8 Blockchain Validation Testing

The blockchain validation endpoint was tested after the demonstration workflows.

The ledger reported:

```text
Ledger Status: VALID
```

Validation checks included:

- Block hashes
- Previous-hash links
- Proof-of-Work requirement
- Merkle Roots

---

### 19.9 Data Structure Visualizer Testing

The Data Structure Visualizer was tested using Block #122.

The visualizer successfully displayed:

```text
Selected Block: #122
Transactions: 500
Tree Height: 10
Merkle Root: Displayed
Calculated Root: Matching
Merkle Status: VERIFIED
```

The visualizer also displayed the hash-linked blockchain relationship between:

```text
Block #122
    |
    v
Block #121
    |
    v
Block #120
```

---

### 19.10 End-to-End Validation

The final end-to-end demonstration successfully covered:

```text
Hospital A
   |
   +--> EHR Retrieval
   |
   +--> Integrity Verification
   |
   +--> Tamper Detection
   |
   +--> Restore
   |
   v
Hospital B
   |
   +--> Cross-Hospital Verification
   |
   v
Insurance
   |
   +--> Claim Verification
   |
   v
Admin
   |
   +--> Blockchain
   +--> Audit
   +--> Benchmark
   |
   v
DSA Visualizer
```

---

## 20. Performance Benchmarking

The project includes a performance benchmark endpoint to demonstrate the computational characteristics of the implemented algorithms.

The benchmark is available through:

```text
GET /api/performance/benchmark
```

---

### 20.1 SHA-256 Benchmark

The SHA-256 benchmark measures the time required to hash healthcare-style data.

Conceptually:

```text
Input Data
    |
    v
SHA-256
    |
    v
Execution Time
```

Since SHA-256 processes the complete input, the theoretical time complexity is:

```text
O(n)
```

where `n` represents the size of the input.

---

### 20.2 Merkle Tree Construction Benchmark

The benchmark measures the time required to construct a Merkle Tree from a collection of transaction hashes.

For `n` leaves:

```text
Construction Complexity = O(n)
```

The benchmark provides practical runtime information for the implementation.

---

### 20.3 Merkle Proof Benchmark

The system also benchmarks Merkle proof generation and verification.

The theoretical proof complexity is:

```text
O(log n)
```

because only the sibling hashes along the path from the leaf to the root are required.

---

### 20.4 Hash Table vs Linear Search

One of the important DSA comparisons is between:

```text
Custom Hash Table Lookup
```

and:

```text
Linear Search
```

Conceptually:

```text
Linear Search
----------------
Item 1
Item 2
Item 3
...
Item n

Search -> O(n)
```

versus:

```text
Hash Table
----------------
Key
 |
 v
Hash Function
 |
 v
Bucket
 |
 v
Entry

Average Search -> O(1)
```

The benchmark demonstrates the practical performance difference between the two approaches.

---

### 20.5 Blockchain Validation Benchmark

The benchmark also measures the time required to validate the blockchain.

Validation includes:

```text
Block Hash Checking
       +
Previous Hash Checking
       +
Proof-of-Work Checking
       +
Merkle Root Checking
```

The resulting execution time provides an empirical measurement for the implemented blockchain.

---

### 20.6 Why Benchmarking Is Included

Benchmarking demonstrates that the project is not only a visual blockchain application but also an implementation-focused DSA project.

It provides measurable evidence for:

- Algorithm execution
- Data structure lookup
- Cryptographic operations
- Merkle verification
- Blockchain validation

The benchmark values are environment-dependent and should therefore be interpreted as measurements of the tested machine rather than universal performance values.

---

## 21. Security and Integrity Considerations

The project demonstrates several mechanisms that contribute to healthcare record integrity.

### 21.1 Cryptographic Hashing

SHA-256 provides a fixed-length cryptographic digest of the canonical healthcare record.

A modification to the record changes the resulting digest.

```text
Original Record
      |
      v
Hash A

Modified Record
      |
      v
Hash B
```

If:

```text
Hash A != Hash B
```

the current record does not match the original cryptographic commitment.

---

### 21.2 Merkle Tree Integrity

The Merkle Tree provides a compact cryptographic representation of multiple transactions.

The Merkle Root summarizes the hashes of the transactions included in the block.

A transaction can be verified using its Merkle proof.

```text
Transaction
     |
     v
Merkle Proof
     |
     v
Calculated Root
     |
     v
Compare with Stored Root
```

---

### 21.3 Hash-Linked Blockchain

Each blockchain block stores the hash of the previous block.

```text
Block 1
   |
   | Hash
   v
Block 2
   |
   | Hash
   v
Block 3
```

Changing a previous block would cause its hash to change, which would affect the corresponding previous-hash relationship of the following block.

---

### 21.4 Separation of Data and Integrity Metadata

The prototype does not store the complete healthcare record inside the blockchain.

Instead:

```text
Healthcare Data
      |
      v
SQLite Database

Integrity Metadata
      |
      v
Merkle Tree + Blockchain
```

This design keeps the blockchain representation relatively small while still allowing integrity verification against the stored healthcare data.

---

### 21.5 Role-Based Demonstration

The application provides different interfaces for:

```text
HOSPITAL
INSURANCE
ADMIN
```

The role-specific frontend determines which demonstration workflows are available to each user.

The project should be understood as a functional educational prototype; production healthcare deployments would require substantially stronger authentication, authorization, key management, privacy controls, compliance mechanisms, and infrastructure security.

---

### 21.6 Audit Trail

Important system activities are recorded in an audit trail.

This provides an additional layer of accountability.

Example:

```text
Login
  |
  v
Patient Search
  |
  v
EHR Access
  |
  v
Verification
  |
  v
Logout
```

The audit trail can be inspected through the Admin interface.

---

### 21.7 Synthetic Healthcare Data

The project uses synthetic healthcare data for development and demonstration.

This avoids making real patient medical records part of the application dataset.

The project is therefore intended for:

- Academic demonstration
- DSA learning
- Algorithm evaluation
- Prototype development
- Software testing

It is not presented as a production-ready clinical information system.

## 22. Limitations

Although the project demonstrates the required DSA and integrity concepts, it is an educational prototype and has several limitations.

### 22.1 Educational Blockchain

The blockchain implemented in this project is a local educational hash-linked ledger.

It demonstrates:

- Block hashing
- Previous-hash linking
- Merkle Roots
- Proof of Work
- Blockchain validation

However, it is not a distributed blockchain network with multiple independent nodes and consensus protocols.

---

### 22.2 Local Database

The prototype uses SQLite as its persistent database.

This is suitable for:

- Development
- Testing
- Academic demonstrations
- Local prototypes

A production healthcare deployment would typically require a more robust database architecture and infrastructure.

---

### 22.3 Demonstration Authentication

The project uses predefined demonstration accounts.

The authentication mechanism is intended to demonstrate role separation and application workflows rather than provide a production-grade identity management system.

A production implementation would require mechanisms such as:

- Strong identity management
- Multi-factor authentication
- Secure password policies
- Token/session management
- Account lifecycle management
- Credential rotation

---

### 22.4 Frontend-Level Role Separation

The current prototype provides role-specific user interfaces for the demonstration.

The roles include:

```text
Hospital
Insurance
Admin
```

The project should not be considered a complete enterprise-grade authorization system.

A production deployment would require authorization enforcement at every protected backend operation as well as centralized identity and access management.

---

### 22.5 No Real Patient Data

The system uses synthetic healthcare data.

Therefore, the project does not represent the complete requirements associated with handling real clinical data.

Real healthcare deployments would need appropriate:

- Privacy controls
- Regulatory compliance
- Data retention policies
- Consent mechanisms
- Access controls
- Encryption
- Security monitoring

---

### 22.6 Controlled Tamper Restoration

The restore operation exists specifically for the academic demonstration.

The intended demonstration is:

```text
Valid Record
     |
     v
Tamper
     |
     v
Detect
     |
     v
Restore
     |
     v
Verify Again
```

In a real system, historical clinical corrections should be handled through authorized versioning and auditable correction workflows rather than simply replacing the modified value.

---

### 22.7 Performance Environment Dependence

Benchmark results depend on the hardware and software environment in which the application is executed.

Therefore, benchmark timings should be treated as experimental measurements rather than universal performance guarantees.

---

### 22.8 No Distributed Healthcare Network

The current project demonstrates multiple healthcare organizations through role-based application workflows.

It does not create physically distributed hospital servers communicating through a decentralized blockchain network.

The organizations are represented within the same educational prototype environment.

---

## 23. Future Enhancements

The current implementation can be extended in several directions.

### 23.1 Distributed Blockchain Nodes

The local blockchain could be extended into a multi-node architecture.

For example:

```text
Hospital A Node
      |
      +----------------+
      |                |
      v                v
Hospital B Node    Insurance Node
      |                |
      +--------+-------+
               |
               v
        Shared Ledger
```

Each organization could maintain a blockchain node and participate in a consensus protocol.

---

### 23.2 Advanced Access Control

The system could be extended with more granular access control.

Possible roles include:

```text
Patient
Doctor
Hospital
Laboratory
Insurance
Pharmacy
Administrator
Researcher
```

Permissions could be defined at:

- Patient level
- Record level
- Organization level
- Data category level
- Operation level

---

### 23.3 Patient-Controlled Access

A future version could provide a patient portal where patients can view and manage authorized access to their records.

A possible workflow would be:

```text
Patient
   |
   v
Access Request
   |
   v
Patient Approval
   |
   v
Hospital / Insurance
   |
   v
Authorized EHR Access
```

This functionality is intentionally outside the current prototype scope.

---

### 23.4 Privacy-Preserving Metadata

The system could be enhanced to minimize the amount of identifiable information exposed during verification.

Potential approaches could include:

- Pseudonymous patient identifiers
- Encrypted metadata
- Selective disclosure
- Zero-knowledge techniques
- Privacy-preserving proofs

---

### 23.5 Batch Verification

Multiple records could be verified together using a Merkle Root rather than individually processing every record.

For example:

```text
Record 1
Record 2
Record 3
Record 4
   |
   v
Merkle Tree
   |
   v
Single Merkle Root
   |
   v
Blockchain
```

This could improve verification efficiency for large groups of healthcare records.

---

### 23.6 Parallel Verification

Verification of independent healthcare records could be performed concurrently.

For example:

```text
             Verification Request
                     |
        +------------+------------+
        |            |            |
        v            v            v
     Record 1     Record 2     Record 3
        |            |            |
        v            v            v
      Hash         Hash         Hash
        |            |            |
        +------------+------------+
                     |
                     v
              Verification Result
```

This could be useful when validating large collections of records.

---

### 23.7 Improved Blockchain Consensus

The current Proof-of-Work mechanism is intentionally lightweight.

A future version could investigate other consensus approaches depending on the intended healthcare network architecture.

---

### 23.8 Cloud Deployment

The application could be deployed using a cloud architecture.

A possible architecture could contain:

```text
Web Frontend
      |
      v
Cloud API
      |
      +--------> Database
      |
      +--------> Blockchain Service
      |
      +--------> Audit Service
```

This would allow the system to be accessed by geographically distributed healthcare organizations.

---

### 23.9 Advanced Monitoring

Future versions could provide monitoring dashboards for:

- Blockchain health
- Verification failures
- Suspicious access
- Failed authentication
- Tampering attempts
- API activity
- Performance metrics

---

### 23.10 Larger Healthcare Datasets

The prototype could be evaluated using larger synthetic healthcare datasets.

Possible future experiments could compare:

```text
Small Dataset
      vs
Medium Dataset
      vs
Large Dataset
```

and measure:

- Hashing time
- Merkle construction time
- Proof verification time
- Hash Table lookup
- Blockchain validation
- Database retrieval

---

### 23.11 Digital Signatures

Digital signatures could be added to provide stronger organizational authentication and non-repudiation.

A possible workflow would be:

```text
Hospital A
    |
    v
Sign Record
    |
    v
Store Record Hash
    |
    v
Blockchain
    |
    v
Hospital B
    |
    v
Verify Signature + Integrity
```

This would complement the existing SHA-256 and Merkle-based integrity mechanisms.

---

## 24. Conclusion

This project demonstrates how Data Structures and Algorithms can be applied to a healthcare record integrity problem.

The system combines:

```text
SHA-256
   +
Merkle Trees
   +
Blockchain
   +
Hash Tables
   +
Linked Lists
   +
SQLite
   +
FastAPI
   +
Web Interface
```

The central integrity pipeline is:

```text
Healthcare Record
       |
       v
Canonical Representation
       |
       v
SHA-256
       |
       v
Record Hash
       |
       v
Merkle Tree
       |
       v
Merkle Root
       |
       v
Blockchain
       |
       v
Verification
```

The prototype demonstrates that a healthcare record can be independently checked against a previously stored cryptographic commitment.

The implemented system successfully demonstrates:

- Patient search
- Longitudinal EHR retrieval
- SHA-256 record hashing
- Merkle Tree construction
- Merkle proof verification
- Hash-linked blockchain
- Blockchain validation
- Clinical tamper detection
- Billing tamper detection
- Cross-hospital retrieval
- Insurance claim verification
- Audit logging
- Custom Hash Table
- Linked Lists
- Performance benchmarking
- Data Structure visualization

The most important DSA relationship demonstrated by the project is:

```text
Hash Table
    |
    +----> Efficient Lookup

Linked List
    |
    +----> Patient History / Audit Trail

Merkle Tree
    |
    +----> Efficient Integrity Verification

Blockchain
    |
    +----> Tamper-Evident Integrity Ledger
```

The project therefore connects theoretical DSA concepts with a practical healthcare-oriented application while keeping the implementation understandable and demonstrable as a college capstone.

The final system is intended as an **educational functional prototype**, not as a production healthcare platform.

---