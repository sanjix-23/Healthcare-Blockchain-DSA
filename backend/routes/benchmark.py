"""
Performance Benchmark and DSA Complexity API.
Executes live micro-benchmarks on core algorithms and provides theoretical complexity stats.
"""

import time
from fastapi import APIRouter
from core.crypto import sha256_hash
from core.merkle_tree import MerkleTree
from backend.state import AppState

router = APIRouter(prefix="/api/performance", tags=["Performance & DSA Benchmarks"])


@router.get("/benchmark")
def run_live_benchmark():
    """
    Executes live micro-benchmarks across all 5 DSA components and returns
    exact execution latencies alongside asymptotic complexity metadata.
    """
    state = AppState.get_instance()
    results = {}

    # 1. SHA-256 Benchmark (1,000 hashes)
    sample_text = "Canonical_EHR_Record_Package_Patient_P000001_Encounter_Visit_2026-09-19"
    t0 = time.perf_counter()
    for _ in range(1000):
        _ = sha256_hash(sample_text)
    t_sha = (time.perf_counter() - t0) / 1000 * 1e6  # Microseconds per hash

    results["sha256_microsecond"] = round(t_sha, 3)
    results["sha256_complexity"] = "O(L) where L is input byte length"

    # 2. Merkle Tree Construction Benchmark (Sizes: 10, 100, 500, 1000)
    merkle_benchmarks = {}
    for size in [10, 100, 500, 1000]:
        sample_leaves = [sha256_hash(f"leaf_record_{i}") for i in range(size)]
        t_start = time.perf_counter()
        tree = MerkleTree(sample_leaves)
        merkle_benchmarks[f"{size}_leaves_ms"] = round((time.perf_counter() - t_start) * 1000, 4)

    results["merkle_construction"] = merkle_benchmarks
    results["merkle_construction_complexity"] = "O(N) bottom-up linear build"

    # 3. Merkle Proof Generation & Verification (500 leaves)
    leaves_500 = [sha256_hash(f"leaf_record_{i}") for i in range(500)]
    tree_500 = MerkleTree(leaves_500)
    root_500 = tree_500.get_root()

    t_gen_start = time.perf_counter()
    proof = tree_500.get_proof(250)
    t_proof_gen = (time.perf_counter() - t_gen_start) * 1e6  # Microseconds

    t_ver_start = time.perf_counter()
    is_valid = MerkleTree.verify_proof(leaves_500[250], proof, root_500)
    t_proof_ver = (time.perf_counter() - t_ver_start) * 1e6  # Microseconds

    results["merkle_proof_generation_us"] = round(t_proof_gen, 3)
    results["merkle_proof_generation_complexity"] = "O(log N) tree height traversal"
    results["merkle_proof_verification_us"] = round(t_proof_ver, 3)
    results["merkle_proof_verification_complexity"] = "O(log N) pairwise hashing"

    # 4. CustomHashTable vs Linear Scan (Patient Lookup)
    test_pid = "b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85"
    
    # CustomHashTable O(1) lookup
    t_ht_start = time.perf_counter()
    for _ in range(100):
        _ = state.patient_id_table.get(test_pid)
    t_hash_table = (time.perf_counter() - t_ht_start) / 100 * 1e6

    # Linear list scan O(N) lookup
    all_patients_list = state.patient_id_table.values()
    t_list_start = time.perf_counter()
    for _ in range(100):
        for p in all_patients_list:
            if p["id"] == test_pid:
                break
    t_linear_scan = (time.perf_counter() - t_list_start) / 100 * 1e6

    results["hash_table_lookup_us"] = round(t_hash_table, 3)
    results["hash_table_complexity"] = "O(1) average time via bucket chaining"
    results["linear_scan_lookup_us"] = round(t_linear_scan, 3)
    results["linear_scan_complexity"] = "O(N) sequential search"
    results["hash_table_speedup_factor"] = round(t_linear_scan / max(0.001, t_hash_table), 1)

    # 5. Full Blockchain Ledger Validation (All 124 blocks)
    t_chain_start = time.perf_counter()
    chain_valid, _ = state.blockchain.is_valid_chain()
    t_chain_val = (time.perf_counter() - t_chain_start) * 1000

    results["blockchain_validation_ms"] = round(t_chain_val, 3)
    results["blockchain_validation_complexity"] = "O(B * K) where B is block count and K is transactions per block"
    results["blockchain_append_complexity"] = "O(1) for linked structure"
    results["total_blocks_checked"] = len(state.blockchain.chain)

    return {
        "timestamp": time.time(),
        "benchmarks": results
    }
