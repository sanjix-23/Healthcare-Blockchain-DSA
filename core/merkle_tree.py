"""
Core Merkle Tree Implementation for Healthcare Blockchain DSA Capstone.

A Merkle Tree is a complete binary hash tree where:
- Every leaf node contains the cryptographic hash of an EHR record.
- Every internal node contains the cryptographic hash of its concatenated children:
      H(parent) = SHA-256(H(left_child) + H(right_child))
- The single Merkle Root summarizes the integrity of all transactions in a block.

DSA Complexities:
- Tree Construction: O(N) where N is the number of leaves
- Merkle Proof Generation: O(log N) path traversal
- Merkle Proof Verification: O(log N) pairwise hashing
- Space Complexity: O(N) storing the binary tree nodes in memory
"""

from typing import List, Optional, Tuple, Dict
from core.crypto import sha256_hash


class MerkleNode:
    """
    Represents a single node within the Merkle Tree.
    """
    def __init__(self, hash_val: str, left: Optional['MerkleNode'] = None, right: Optional['MerkleNode'] = None):
        self.hash: str = hash_val
        self.left: Optional['MerkleNode'] = left
        self.right: Optional['MerkleNode'] = right
        self.parent: Optional['MerkleNode'] = None
        
        if self.left:
            self.left.parent = self
        if self.right:
            self.right.parent = self

    @property
    def is_leaf(self) -> bool:
        return self.left is None and self.right is None


class MerkleTree:
    """
    Complete Binary Merkle Tree built from scratch.
    """
    def __init__(self, leaves: Optional[List[str]] = None):
        self.leaves: List[str] = []
        self.leaf_nodes: List[MerkleNode] = []
        self.root: Optional[MerkleNode] = None
        self.levels: List[List[MerkleNode]] = []
        
        if leaves:
            self.build(leaves)

    def build(self, leaves: List[str]) -> None:
        """
        Builds the Merkle Tree bottom-up from an array of leaf hashes.
        Time Complexity: O(N)
        Space Complexity: O(N)
        """
        self.leaves = list(leaves)
        if not self.leaves:
            self.root = None
            self.levels = []
            self.leaf_nodes = []
            return

        # Level 0: Leaf nodes
        current_level: List[MerkleNode] = [MerkleNode(h) for h in self.leaves]
        self.leaf_nodes = list(current_level)
        self.levels = [current_level]

        # Iteratively build parent levels until a single root remains
        while len(current_level) > 1:
            next_level: List[MerkleNode] = []
            num_nodes = len(current_level)

            for i in range(0, num_nodes, 2):
                left = current_level[i]
                # If odd number of nodes at this level, duplicate the last node to maintain binary completeness
                if i + 1 < num_nodes:
                    right = current_level[i + 1]
                else:
                    right = MerkleNode(left.hash, left.left, left.right)

                # Parent hash = SHA-256(left.hash + right.hash)
                parent_hash = sha256_hash(left.hash + right.hash)
                parent_node = MerkleNode(parent_hash, left, right)
                next_level.append(parent_node)

            self.levels.append(next_level)
            current_level = next_level

        self.root = current_level[0]

    def get_root(self) -> str:
        """
        Returns 64-character hexadecimal SHA-256 Merkle root.
        """
        return self.root.hash if self.root else ""

    def get_proof(self, leaf_index: int) -> List[Dict[str, str]]:
        """
        Generates the Merkle Audit Path (Merkle Proof) for a given leaf index.
        Returns a list of dictionaries with sibling hash and direction:
        [{'hash': '<sibling_hash>', 'direction': 'left' | 'right'}, ...]
        
        Time Complexity: O(log N)
        Space Complexity: O(log N)
        """
        if not self.levels or leaf_index < 0 or leaf_index >= len(self.leaf_nodes):
            raise IndexError(f"Leaf index {leaf_index} out of bounds (0 to {len(self.leaf_nodes)-1})")

        proof: List[Dict[str, str]] = []
        idx = leaf_index

        for level in self.levels[:-1]:  # Exclude root level
            is_right_child = (idx % 2 == 1)
            
            if is_right_child:
                # Sibling is on the left
                sibling_idx = idx - 1
                sibling_hash = level[sibling_idx].hash
                proof.append({"hash": sibling_hash, "direction": "left"})
            else:
                # Sibling is on the right
                if idx + 1 < len(level):
                    sibling_hash = level[idx + 1].hash
                else:
                    # Self-duplicated odd node
                    sibling_hash = level[idx].hash
                proof.append({"hash": sibling_hash, "direction": "right"})

            idx //= 2

        return proof

    @staticmethod
    def verify_proof(leaf_hash: str, proof: List[Dict[str, str]], expected_root: str) -> bool:
        """
        Verifies a Merkle proof against an expected Merkle root.
        Recomputes hash path upward from leaf to root.
        
        Time Complexity: O(log N)
        Space Complexity: O(1)
        """
        current_hash = leaf_hash

        for step in proof:
            sibling_hash = step["hash"]
            direction = step["direction"]

            if direction == "left":
                # Sibling + Current
                current_hash = sha256_hash(sibling_hash + current_hash)
            elif direction == "right":
                # Current + Sibling
                current_hash = sha256_hash(current_hash + sibling_hash)
            else:
                raise ValueError(f"Invalid direction '{direction}' in Merkle proof")

        return current_hash == expected_root
