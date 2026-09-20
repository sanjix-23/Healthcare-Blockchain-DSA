"""
Pydantic Request and Response Schemas for Healthcare Blockchain REST API.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# --- Auth Schemas ---
class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    username: str
    org_id: str
    org_name: str
    role: str  # 'HOSPITAL', 'INSURANCE', 'ADMIN'
    token: str


# --- Patient Schemas ---
class PatientSearchItem(BaseModel):
    id: str
    first_name: str
    last_name: str
    birthdate: str
    gender: str
    city: str
    state: str
    zip: str
    organizations_visited: List[str] = []


class PatientCreateRequest(BaseModel):
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    birthdate: str = Field(..., description="YYYY-MM-DD")
    gender: str = Field("M", description="M or F")
    race: Optional[str] = "white"
    ethnicity: Optional[str] = "nonhispanic"
    city: str = Field(..., min_length=1)
    state: str = Field(..., min_length=1)
    zip: str = Field(..., min_length=1)


class PatientCreateResponse(BaseModel):
    patient_id: str
    first_name: str
    last_name: str
    message: str


# --- Encounter Schemas ---
class ClinicalConditionInput(BaseModel):
    code: str
    description: str


class ClinicalMedicationInput(BaseModel):
    code: str
    description: str
    dispenses: int = 1
    total_cost: float = 0.0


class ClinicalProcedureInput(BaseModel):
    code: str
    description: str
    base_cost: float = 0.0


class ClinicalImmunizationInput(BaseModel):
    code: str
    description: str


class ClinicalObservationInput(BaseModel):
    category: str = "vital-signs"
    code: str
    description: str
    value: str
    units: str


class ClaimBillingInput(BaseModel):
    payer_id: Optional[str] = None
    total_claim_cost: float = 0.0
    payer_coverage: float = 0.0
    diagnosis_code: Optional[str] = None
    procedure_code: Optional[str] = None
    status: str = "CLOSED"


class EncounterCreateRequest(BaseModel):
    patient_id: str
    organization_id: str
    provider_id: Optional[str] = None
    payer_id: Optional[str] = None
    encounter_class: str = "ambulatory"
    code: Optional[str] = "GENERAL_VISIT"
    description: str
    base_cost: float = 0.0
    conditions: List[ClinicalConditionInput] = []
    medications: List[ClinicalMedicationInput] = []
    procedures: List[ClinicalProcedureInput] = []
    immunizations: List[ClinicalImmunizationInput] = []
    observations: List[ClinicalObservationInput] = []
    claim: Optional[ClaimBillingInput] = None


class EncounterCreateResponse(BaseModel):
    encounter_id: str
    patient_id: str
    record_hash: str
    block_index: int
    merkle_leaf_index: int
    merkle_root: str
    block_hash: str
    status: str


# --- Integrity Verification Schemas ---
class VerificationResponse(BaseModel):
    encounter_id: str
    patient_id: str
    organization_id: str
    current_hash: str
    stored_hash: str
    hash_match: bool
    block_index: int
    merkle_root: str
    block_hash: str
    merkle_proof: List[Dict[str, str]]
    merkle_proof_valid: bool
    blockchain_valid: bool
    integrity_status: str  # 'VERIFIED' or 'TAMPERED'
    tamper_details: Optional[str] = None


# --- Tamper Simulation Schemas ---
class TamperClinicalRequest(BaseModel):
    encounter_id: str
    field: str = "description"  # 'description' or 'condition'
    new_value: str = "TAMPERED DIAGNOSIS: SEVERE UNREPORTED CONDITION"


class TamperBillingRequest(BaseModel):
    encounter_id: str
    field: str = "total_claim_cost"  # 'total_claim_cost' or 'procedure_code'
    new_value: Any = 99999.00


class TamperRestoreRequest(BaseModel):
    encounter_id: str
