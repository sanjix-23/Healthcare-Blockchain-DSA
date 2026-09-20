"""
Core Cryptographic Module for Healthcare Blockchain DSA Capstone.

Implements SHA-256 hashing and deterministic canonical JSON serialization
for EHR record packages and blockchain components.

Complexity:
- sha256_hash: Time O(L) where L is input byte length; Space O(1) [fixed 32 bytes / 64 hex chars]
- canonical_json: Time O(M log M) where M is total keys/values due to sorting; Space O(M)
"""

import hashlib
import json
from typing import Any, Union


def canonical_json(data: Union[dict, list]) -> str:
    """
    Serializes a dictionary or list into a deterministic canonical JSON string.
    Ensures that identical clinical records always produce identical hashes:
    - Sorts dictionary keys recursively (sort_keys=True)
    - Eliminates arbitrary whitespace (separators=(',', ':'))
    - Standardizes numeric float representations
    """
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_hash(data: Union[str, bytes]) -> str:
    """
    Computes standard SHA-256 cryptographic digest of given string or bytes.
    Returns 64-character lowercase hexadecimal string.
    
    Properties:
    - Preimage resistance: computationally infeasible to invert H(x) -> x
    - Collision resistance: computationally infeasible to find x != y such that H(x) == H(y)
    - Avalanche effect: 1-bit input change changes ~50% of output bits
    """
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def hash_record(record: dict) -> str:
    """
    Computes SHA-256 fingerprint of a canonical EHR record package.
    """
    serialized = canonical_json(record)
    return sha256_hash(serialized)
