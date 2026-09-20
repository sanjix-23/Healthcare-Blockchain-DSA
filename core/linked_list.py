"""
Singly Linked List Implementations for Healthcare Blockchain DSA Capstone.

Implements from scratch:
1. PatientHistoryLinkedList: A chronological sequence of medical encounters
   for a specific patient across multiple hospitals.
2. AuditLogLinkedList: An append-only sequential stream of system events,
   verifications, and tamper detection alerts.

DSA Complexity:
- Append Node: O(1) using maintained tail pointer
- Chronological Traversal: O(M) where M is the number of encounters for the patient
- Node Search by ID: O(M) linear scan
- Space Complexity: O(M) linear in total encounter nodes
"""

from typing import Optional, List, Dict, Any


class HistoryNode:
    """
    Singly linked list node storing one clinical encounter package in a patient's timeline.
    """
    def __init__(
        self,
        encounter_id: str,
        patient_id: str,
        organization_id: str,
        provider_id: str,
        start_time: str,
        stop_time: str,
        encounter_class: str,
        description: str,
        base_cost: float,
        record_hash: str,
        block_index: Optional[int] = None,
        merkle_leaf_index: Optional[int] = None,
        conditions: Optional[List[Dict[str, Any]]] = None,
        medications: Optional[List[Dict[str, Any]]] = None,
        procedures: Optional[List[Dict[str, Any]]] = None,
        immunizations: Optional[List[Dict[str, Any]]] = None,
        observations: Optional[List[Dict[str, Any]]] = None,
        claims: Optional[List[Dict[str, Any]]] = None
    ):
        self.encounter_id: str = encounter_id
        self.patient_id: str = patient_id
        self.organization_id: str = organization_id
        self.provider_id: str = provider_id
        self.start_time: str = start_time
        self.stop_time: str = stop_time
        self.encounter_class: str = encounter_class
        self.description: str = description
        self.base_cost: float = base_cost
        self.record_hash: str = record_hash
        self.block_index: Optional[int] = block_index
        self.merkle_leaf_index: Optional[int] = merkle_leaf_index
        
        self.conditions: List[Dict[str, Any]] = conditions or []
        self.medications: List[Dict[str, Any]] = medications or []
        self.procedures: List[Dict[str, Any]] = procedures or []
        self.immunizations: List[Dict[str, Any]] = immunizations or []
        self.observations: List[Dict[str, Any]] = observations or []
        self.claims: List[Dict[str, Any]] = claims or []

        self.next: Optional['HistoryNode'] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the HistoryNode into a dictionary format for API transmission and UI rendering.
        """
        return {
            "encounter_id": self.encounter_id,
            "patient_id": self.patient_id,
            "organization_id": self.organization_id,
            "provider_id": self.provider_id,
            "start_time": self.start_time,
            "stop_time": self.stop_time,
            "encounter_class": self.encounter_class,
            "description": self.description,
            "base_cost": self.base_cost,
            "record_hash": self.record_hash,
            "block_index": self.block_index,
            "merkle_leaf_index": self.merkle_leaf_index,
            "conditions": self.conditions,
            "medications": self.medications,
            "procedures": self.procedures,
            "immunizations": self.immunizations,
            "observations": self.observations,
            "claims": self.claims
        }


class PatientHistoryLinkedList:
    """
    Singly linked list connecting a patient's chronological healthcare encounters.
    Maintains head and tail pointers for O(1) append.
    """
    def __init__(self):
        self.head: Optional[HistoryNode] = None
        self.tail: Optional[HistoryNode] = None
        self.size: int = 0

    def append(self, node: HistoryNode) -> None:
        """
        Appends a new encounter node to the end of the patient's timeline.
        Time Complexity: O(1)
        """
        if not self.head:
            self.head = node
            self.tail = node
        else:
            assert self.tail is not None
            self.tail.next = node
            self.tail = node
        self.size += 1

    def find(self, encounter_id: str) -> Optional[HistoryNode]:
        """
        Linearly searches the patient's history for an encounter by ID.
        Time Complexity: O(M) where M is total encounters for this patient.
        """
        curr = self.head
        while curr:
            if curr.encounter_id == encounter_id:
                return curr
            curr = curr.next
        return None

    def to_list(self) -> List[Dict[str, Any]]:
        """
        Traverses the linked list chronologically and returns a list of dictionaries.
        Time Complexity: O(M)
        """
        records = []
        curr = self.head
        while curr:
            records.append(curr.to_dict())
            curr = curr.next
        return records

    def __len__(self) -> int:
        return self.size


class AuditNode:
    """
    Singly linked list node storing an access or verification event.
    """
    def __init__(
        self,
        event_id: int,
        timestamp: str,
        org_id: str,
        action: str,
        patient_id: Optional[str] = None,
        record_id: Optional[str] = None,
        status: str = "SUCCESS",
        details: str = ""
    ):
        self.event_id: int = event_id
        self.timestamp: str = timestamp
        self.org_id: str = org_id
        self.action: str = action
        self.patient_id: Optional[str] = patient_id
        self.record_id: Optional[str] = record_id
        self.status: str = status
        self.details: str = details
        self.next: Optional['AuditNode'] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "org_id": self.org_id,
            "action": self.action,
            "patient_id": self.patient_id,
            "record_id": self.record_id,
            "status": self.status,
            "details": self.details
        }


class AuditLogLinkedList:
    """
    Append-only singly linked list maintaining an in-memory audit trail.
    """
    def __init__(self):
        self.head: Optional[AuditNode] = None
        self.tail: Optional[AuditNode] = None
        self.size: int = 0

    def append(self, node: AuditNode) -> None:
        """
        Appends an audit log event.
        Time Complexity: O(1)
        """
        if not self.head:
            self.head = node
            self.tail = node
        else:
            assert self.tail is not None
            self.tail.next = node
            self.tail = node
        self.size += 1

    def to_list(self) -> List[Dict[str, Any]]:
        """
        Returns all audit events in chronological order.
        Time Complexity: O(E)
        """
        events = []
        curr = self.head
        while curr:
            events.append(curr.to_dict())
            curr = curr.next
        return events

    def __len__(self) -> int:
        return self.size
