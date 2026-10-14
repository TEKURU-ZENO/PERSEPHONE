"""
Clinical Evidence Agent and Safety Gate Package (Phase 4 AI Component).
"""

from backend.python.compute.clinical_evidence.schemas import (
    Citation,
    ClinicalEvaluationCase,
    EvidenceLevel,
    EvidenceRecommendation,
    PatientClinicalProfile,
    SafetyCheckResult,
)
from backend.python.compute.clinical_evidence.safety_gate import DeterministicSafetyGate
from backend.python.compute.clinical_evidence.evidence_agent import EvidenceAgent

__all__ = [
    "Citation",
    "ClinicalEvaluationCase",
    "EvidenceLevel",
    "EvidenceRecommendation",
    "PatientClinicalProfile",
    "SafetyCheckResult",
    "DeterministicSafetyGate",
    "EvidenceAgent",
]
