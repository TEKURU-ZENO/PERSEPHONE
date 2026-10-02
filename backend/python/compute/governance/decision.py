"""
Immutable Governance Decision Module for PERSEPHONE Governance Platform.
Defines the authoritative, tamper-evident GovernanceDecision data structure
representing the definitive gate verdict prior to report generation.
"""
from typing import Dict, List, Any, Optional
import hashlib
import time
import json


class GovernanceDecision:
    """
    Immutable Governance Decision Certificate.
    Once instantiated, attributes cannot be modified.
    Downstream agents (Explainability, Report Generator) consume this object as read-only authority.
    """

    def __init__(
        self,
        decision_status: str,
        confidence: float,
        abstention_code: Optional[str],
        reason: str,
        safety_findings: List[Dict[str, Any]],
        validation_findings: List[Dict[str, Any]],
        contradiction_findings: List[Dict[str, Any]],
        uncertainty: Dict[str, Any],
        drift_status: str,
        evidence_refs: List[str],
        rule_versions: List[str],
        model_versions: List[str],
        required_actions: List[str],
        clinician_guidance: str = "",
        timestamp: Optional[str] = None
    ):
        self._decision_status = decision_status
        self._confidence = float(confidence)
        self._abstention_code = abstention_code
        self._reason = reason
        self._safety_findings = list(safety_findings)
        self._validation_findings = list(validation_findings)
        self._contradiction_findings = list(contradiction_findings)
        self._uncertainty = dict(uncertainty)
        self._drift_status = drift_status
        self._evidence_refs = list(evidence_refs)
        self._rule_versions = list(rule_versions)
        self._model_versions = list(model_versions)
        self._required_actions = list(required_actions)
        self._clinician_guidance = clinician_guidance
        self._timestamp = timestamp or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # Cryptographic provenance hash
        payload = (
            f"GOV_DECISION|{decision_status}|{self._confidence:.4f}|{abstention_code or 'NONE'}|"
            f"{reason}|{self._drift_status}|{sorted(self._evidence_refs)}|{sorted(self._rule_versions)}|"
            f"{sorted(self._model_versions)}|{self._timestamp}"
        )
        self._provenance_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()
        self._locked = True

    def __setattr__(self, name, value):
        if getattr(self, "_locked", False):
            raise AttributeError(f"GovernanceDecision is immutable. Cannot modify attribute '{name}'.")
        super().__setattr__(name, value)

    @property
    def decision_status(self) -> str:
        return self._decision_status

    @property
    def confidence(self) -> float:
        return self._confidence

    @property
    def abstention_code(self) -> Optional[str]:
        return self._abstention_code

    @property
    def reason(self) -> str:
        return self._reason

    @property
    def safety_findings(self) -> List[Dict[str, Any]]:
        return list(self._safety_findings)

    @property
    def validation_findings(self) -> List[Dict[str, Any]]:
        return list(self._validation_findings)

    @property
    def contradiction_findings(self) -> List[Dict[str, Any]]:
        return list(self._contradiction_findings)

    @property
    def uncertainty(self) -> Dict[str, Any]:
        return dict(self._uncertainty)

    @property
    def drift_status(self) -> str:
        return self._drift_status

    @property
    def evidence_refs(self) -> List[str]:
        return list(self._evidence_refs)

    @property
    def provenance_hash(self) -> str:
        return self._provenance_hash

    @property
    def rule_versions(self) -> List[str]:
        return list(self._rule_versions)

    @property
    def model_versions(self) -> List[str]:
        return list(self._model_versions)

    @property
    def timestamp(self) -> str:
        return self._timestamp

    @property
    def required_actions(self) -> List[str]:
        return list(self._required_actions)

    @property
    def clinician_guidance(self) -> str:
        return self._clinician_guidance

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_status": self._decision_status,
            "confidence": self._confidence,
            "abstention_code": self._abstention_code,
            "reason": self._reason,
            "safety_findings": self._safety_findings,
            "validation_findings": self._validation_findings,
            "contradiction_findings": self._contradiction_findings,
            "uncertainty": self._uncertainty,
            "drift_status": self._drift_status,
            "evidence_refs": self._evidence_refs,
            "provenance_hash": self._provenance_hash,
            "rule_versions": self._rule_versions,
            "model_versions": self._model_versions,
            "timestamp": self._timestamp,
            "required_actions": self._required_actions,
            "clinician_guidance": self._clinician_guidance
        }
