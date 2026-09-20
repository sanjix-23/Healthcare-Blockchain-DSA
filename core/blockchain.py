"""
Local Educational Blockchain Ledger Prototype for Healthcare Blockchain DSA Capstone.

Implements a hash-linked blockchain data structure where:
- Each block is cryptographically linked to its predecessor via previous_hash.
- Transactions within a block are summarized into an immutable Merkle Root.
- A lightweight Proof-of-Work (PoW) mechanism demonstrates consensus and block sealing.
- Complete chain validation verifies all hash-links, Merkle roots, and PoW nonces.

Terminology:
This is a local educational blockchain ledger prototype and hash-linked data structure
designed for academic verification and viva demonstration, not a production decentralized network.

Complexity Analysis:
- Block Append: O(1) in the linked structure.
- Mining Complexity: Probabilistic / expected work dependent on difficulty target d.
  Each nonce attempt requires exactly one SHA-256 computation over the block header.
  With hexadecimal leading zero target '0'*d, expected trials E[hashes] = 16^d.
  For demo difficulty d=2: E[trials] = 16^2 = 256 hash operations (~1-5 ms execution).
- Chain Validation: O(B * K) where B is the number of blocks and K is transactions per block.
- Space Complexity: O(B * K) storing block headers and transaction records.
"""

import time
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple, Any
from core.crypto import sha256_hash, canonical_json
from core.merkle_tree import MerkleTree


class Block:
    """
    Represents a single block in the educational hash-linked blockchain.
    """
    def __init__(
        self,
        index: int,
        timestamp: str,
        previous_hash: str,
        merkle_root: str,
        transactions: List[Dict[str, Any]],
        nonce: int = 0,
        miner_org: str = "SYSTEM",
        block_hash: str = ""
    ):
        self.index: int = index
        self.timestamp: str = timestamp
        self.previous_hash: str = previous_hash
        self.merkle_root: str = merkle_root
        self.transactions: List[Dict[str, Any]] = transactions
        self.nonce: int = nonce
        self.miner_org: str = miner_org
        self.block_hash: str = block_hash

        if not self.block_hash:
            self.block_hash = self.compute_hash()

    def compute_hash(self) -> str:
        """
        Computes SHA-256 hash over the block header components:
        header = index + timestamp + previous_hash + merkle_root + nonce
        """
        header_str = f"{self.index}:{self.timestamp}:{self.previous_hash}:{self.merkle_root}:{self.nonce}"
        return sha256_hash(header_str)

    def mine(self, difficulty: int = 2) -> None:
        """
        Lightweight Proof-of-Work (PoW) consensus simulation.
        Finds a nonce such that compute_hash() starts with '0'*difficulty.
        
        Probabilistic Complexity:
        Each iteration requires 1 SHA-256 hash calculation.
        Expected number of trials = 16^difficulty.
        For difficulty=2, expected ~256 hash trials (~2-5ms).
        """
        target_prefix = "0" * difficulty
        self.nonce = 0
        current_hash = self.compute_hash()

        while not current_hash.startswith(target_prefix):
            self.nonce += 1
            current_hash = self.compute_hash()

        self.block_hash = current_hash

    def to_dict(self) -> Dict[str, Any]:
        """
        Returns dictionary representation of the block.
        """
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "merkle_root": self.merkle_root,
            "transactions": self.transactions,
            "nonce": self.nonce,
            "miner_org": self.miner_org,
            "block_hash": self.block_hash,
            "tx_count": len(self.transactions)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Block':
        """
        Reconstructs a Block object from a dictionary.
        """
        return cls(
            index=data["index"],
            timestamp=data["timestamp"],
            previous_hash=data["previous_hash"],
            merkle_root=data["merkle_root"],
            transactions=data.get("transactions", []),
            nonce=data.get("nonce", 0),
            miner_org=data.get("miner_org", "SYSTEM"),
            block_hash=data.get("block_hash", "")
        )


class Blockchain:
    """
    Educational Hash-Linked Blockchain Data Structure.
    """
    def __init__(self, difficulty: int = 2):
        self.chain: List[Block] = []
        self.difficulty: int = difficulty
        self.pending_transactions: List[Dict[str, Any]] = []

    def create_genesis_block(self, miner_org: str = "GENESIS") -> Block:
        """
        Creates Block #0 (Genesis Block) to anchor the hash chain.
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        genesis_merkle = sha256_hash("HEALTHCARE_BLOCKCHAIN_GENESIS_ROOT")
        
        genesis_block = Block(
            index=0,
            timestamp=timestamp,
            previous_hash="0" * 64,
            merkle_root=genesis_merkle,
            transactions=[],
            nonce=0,
            miner_org=miner_org
        )
        genesis_block.mine(self.difficulty)
        self.chain = [genesis_block]
        return genesis_block

    def get_latest_block(self) -> Block:
        """
        Returns the head block of the blockchain.
        """
        if not self.chain:
            self.create_genesis_block()
        return self.chain[-1]

    def add_block(self, transactions: List[Dict[str, Any]], miner_org: str = "SYSTEM") -> Block:
        """
        Constructs a Merkle tree from transactions, mines the block,
        and appends it to the hash-linked blockchain.
        Time Complexity: O(N) where N is transaction count + expected PoW trials.
        """
        latest = self.get_latest_block()
        next_index = latest.index + 1
        timestamp = datetime.now(timezone.utc).isoformat()

        # Build Merkle Tree from transaction record hashes
        record_hashes = [tx.get("record_hash", "") for tx in transactions]
        merkle_tree = MerkleTree(record_hashes)
        merkle_root = merkle_tree.get_root()

        # Create new Block linked to predecessor's hash
        new_block = Block(
            index=next_index,
            timestamp=timestamp,
            previous_hash=latest.block_hash,
            merkle_root=merkle_root,
            transactions=transactions,
            nonce=0,
            miner_org=miner_org
        )

        # Mine the block to satisfy Proof-of-Work
        new_block.mine(self.difficulty)

        # Append to chain (O(1) append in linked sequence)
        self.chain.append(new_block)
        return new_block

    def is_valid_chain(self) -> Tuple[bool, str]:
        """
        Validates the complete integrity of the educational blockchain ledger:
        1. Genesis block integrity
        2. Block header SHA-256 hashes
        3. previous_hash linkage between consecutive blocks
        4. Proof-of-Work difficulty fulfillment
        5. Internal Merkle tree reconstruction and root match
        
        Time Complexity: O(B * K) where B is block count and K is transactions per block.
        """
        if not self.chain:
            return False, "Blockchain is empty"

        # Validate Genesis Block
        genesis = self.chain[0]
        if genesis.index != 0:
            return False, f"Invalid genesis block index: {genesis.index}"
        if genesis.previous_hash != "0" * 64:
            return False, f"Invalid genesis previous_hash: {genesis.previous_hash}"
        if genesis.compute_hash() != genesis.block_hash:
            return False, "Genesis block hash mismatch"
        if not genesis.block_hash.startswith("0" * self.difficulty):
            return False, f"Genesis block does not satisfy PoW target ('0'*{self.difficulty})"

        # Validate consecutive blocks
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            # 1. Check index increment
            if current.index != previous.index + 1:
                return False, f"Block #{current.index} has discontinuous index after #{previous.index}"

            # 2. Check previous_hash link
            if current.previous_hash != previous.block_hash:
                return False, (
                    f"Hash link broken at Block #{current.index}: "
                    f"previous_hash '{current.previous_hash[:16]}...' != "
                    f"Block #{previous.index} hash '{previous.block_hash[:16]}...'"
                )

            # 3. Check current block header hash
            recomputed_hash = current.compute_hash()
            if current.block_hash != recomputed_hash:
                return False, (
                    f"Block #{current.index} header hash mismatch: "
                    f"stored '{current.block_hash[:16]}...' != recomputed '{recomputed_hash[:16]}...'"
                )

            # 4. Check Proof-of-Work target
            if not current.block_hash.startswith("0" * self.difficulty):
                return False, f"Block #{current.index} does not meet PoW difficulty ({self.difficulty} leading zeros)"

            # 5. Check Merkle Root integrity by reconstructing tree from transactions
            tx_hashes = [tx.get("record_hash", "") for tx in current.transactions]
            recomputed_tree = MerkleTree(tx_hashes)
            recomputed_root = recomputed_tree.get_root()

            if current.merkle_root != recomputed_root:
                return False, (
                    f"Block #{current.index} Merkle root mismatch: "
                    f"stored '{current.merkle_root[:16]}...' != recomputed '{recomputed_root[:16]}...'"
                )

        return True, f"All {len(self.chain)} blocks are cryptographically verified and valid."
