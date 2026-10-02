"""
Clinical Claim module for PERSEPHONE Research Intelligence Platform.
Defines first-class ClinicalClaim objects with explicit evidence IDs, agent provenance, and cryptographic hashes.
"""
import hashlib
import time
from typing import Dict, List, Any, Optional


class ClinicalClaim:
    """
    First-class Clinical Claim entity representing a verified clinical assertion.
    """
    def __init__(
        self,
        claim_id: str,
        patient_id: str,
        statement: str,
        evidence_ids: List[str],
        source_ids: List[str],
        generating_agent: str,
        confidence: float = 0.90,
        evidence_level: str = "Level 1b",
        recommendation_category: Optional[str] = "Category 1",
        created_at: Optional[str] = None,
        source_version: str = "guideline-2026.1",
        grounding_status: str = "UNVERIFIED"
    ):
        self.claim_id = claim_id
        self.patient_id = patient_id
        self.statement = statement
        self.evidence_ids = evidence_ids or []
        self.source_ids = source_ids or []
        self.generating_agent = generating_agent
        self.confidence = float(confidence)
        self.evidence_level = evidence_level
        self.recommendation_category = recommendation_category
        self.created_at = created_at or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self.source_version = source_version
        self.grounding_status = grounding_status

        # Cryptographic claim provenance hash
        hash_payload = (
            f"{claim_id}|{patient_id}|{statement}|{sorted(self.evidence_ids)}|"
            f"{sorted(self.source_ids)}|{generating_agent}|{source_version}|{self.created_at}"
        )
        self.provenance_hash = hashlib.sha256(hash_payload.encode('utf-8')).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "patient_id": self.patient_id,
            "statement": self.statement,
            "evidence_ids": self.evidence_ids,
            "source_ids": self.source_ids,
            "generating_agent": self.generating_agent,
            "confidence": self.confidence,
            "evidence_level": self.evidence_level,
            "recommendation_category": self.recommendation_category,
            "created_at": self.created_at,
            "source_version": self.source_version,
            "grounding_status": self.grounding_status,
            "provenance_hash": self.provenance_hash
        }
