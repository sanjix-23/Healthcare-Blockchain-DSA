"""
Custom Hash Table with Bucket Chaining for Healthcare Blockchain DSA Capstone.

Implements an explicit Hash Table data structure from scratch using:
- A fixed-capacity array of buckets
- Singly Linked List chaining at each bucket for collision resolution (Separate Chaining)
- A polynomial rolling hash function with prime multiplier (31)
- Dynamic rehashing when load factor alpha exceeds 0.75 to preserve O(1) operations.

DSA Complexity:
- Insert (put): Average O(1), Worst O(N) during extreme collision or resize
- Search (get): Average O(1), Worst O(N) if all keys hash to the same bucket
- Delete (delete): Average O(1), Worst O(N)
- Space Complexity: O(K) where K is the number of stored key-value pairs
"""

from typing import Any, List, Optional, Tuple, Dict


class HashNode:
    """
    Singly linked list node for collision resolution via separate chaining.
    """
    def __init__(self, key: str, value: Any, next_node: Optional['HashNode'] = None):
        self.key: str = key
        self.value: Any = value
        self.next: Optional['HashNode'] = next_node


class CustomHashTable:
    """
    Scratch-built Hash Table with bucket chaining.
    """
    DEFAULT_CAPACITY = 1024
    LOAD_FACTOR_THRESHOLD = 0.75

    def __init__(self, initial_capacity: int = DEFAULT_CAPACITY):
        self.capacity: int = max(16, initial_capacity)
        self.buckets: List[Optional[HashNode]] = [None] * self.capacity
        self.size: int = 0

    def _hash(self, key: str) -> int:
        """
        Polynomial rolling hash function:
        hash = sum(ord(c) * (31^i)) mod capacity
        Uses prime multiplier 31 to uniformly distribute strings across buckets.
        """
        hash_val = 0
        prime = 31
        power = 1
        for char in key:
            hash_val = (hash_val + ord(char) * power) % self.capacity
            power = (power * prime) % self.capacity
        return hash_val

    def _resize(self) -> None:
        """
        Doubles table capacity and rehashes all existing entries
        when load factor exceeds threshold (alpha > 0.75).
        """
        old_buckets = self.buckets
        self.capacity *= 2
        self.buckets = [None] * self.capacity
        self.size = 0

        for head in old_buckets:
            curr = head
            while curr:
                self.put(curr.key, curr.value)
                curr = curr.next

    def put(self, key: str, value: Any) -> None:
        """
        Inserts or updates a key-value pair.
        Average Time Complexity: O(1)
        """
        if (self.size + 1) / self.capacity > self.LOAD_FACTOR_THRESHOLD:
            self._resize()

        bucket_idx = self._hash(key)
        curr = self.buckets[bucket_idx]

        # Traverse bucket's linked list to check if key already exists (update)
        while curr:
            if curr.key == key:
                curr.value = value
                return
            curr = curr.next

        # Key does not exist: prepend new HashNode to bucket linked list
        new_node = HashNode(key, value, self.buckets[bucket_idx])
        self.buckets[bucket_idx] = new_node
        self.size += 1

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieves the value associated with key, or returns default if not found.
        Average Time Complexity: O(1)
        """
        bucket_idx = self._hash(key)
        curr = self.buckets[bucket_idx]

        while curr:
            if curr.key == key:
                return curr.value
            curr = curr.next

        return default

    def delete(self, key: str) -> bool:
        """
        Removes the key-value pair from the hash table.
        Returns True if found and deleted, False otherwise.
        Average Time Complexity: O(1)
        """
        bucket_idx = self._hash(key)
        curr = self.buckets[bucket_idx]
        prev: Optional[HashNode] = None

        while curr:
            if curr.key == key:
                if prev is None:
                    # Deleting the head node of this bucket
                    self.buckets[bucket_idx] = curr.next
                else:
                    # Unlinking an internal node
                    prev.next = curr.next
                self.size -= 1
                return True
            prev = curr
            curr = curr.next

        return False

    def contains(self, key: str) -> bool:
        """
        Checks if key exists in hash table.
        """
        return self.get(key) is not None

    def __len__(self) -> int:
        return self.size

    def keys(self) -> List[str]:
        """
        Returns a list of all keys in the hash table.
        """
        result = []
        for head in self.buckets:
            curr = head
            while curr:
                result.append(curr.key)
                curr = curr.next
        return result

    def values(self) -> List[Any]:
        """
        Returns a list of all values in the hash table.
        """
        result = []
        for head in self.buckets:
            curr = head
            while curr:
                result.append(curr.value)
                curr = curr.next
        return result

    def items(self) -> List[Tuple[str, Any]]:
        """
        Returns all (key, value) pairs.
        """
        result = []
        for head in self.buckets:
            curr = head
            while curr:
                result.append((curr.key, curr.value))
                curr = curr.next
        return result

    def get_diagnostics(self) -> Dict[str, Any]:
        """
        Returns internal hash table statistics for viva inspection:
        - Total items, capacity, load factor
        - Non-empty buckets count
        - Maximum bucket chain length (worst collision depth)
        """
        non_empty = 0
        max_chain = 0
        for head in self.buckets:
            if head:
                non_empty += 1
                chain_len = 0
                curr = head
                while curr:
                    chain_len += 1
                    curr = curr.next
                max_chain = max(max_chain, chain_len)

        return {
            "size": self.size,
            "capacity": self.capacity,
            "load_factor": round(self.size / self.capacity, 4),
            "non_empty_buckets": non_empty,
            "max_chain_length": max_chain
        }
