"""
Governance Decision Contract Schema v1.0 for PERSEPHONE OS.
Standardizes clinical governance assessments, abstention categorization,
and clinician-support review statuses.
"""
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass, field
import hashlib
import time


class GovernanceStatus(str, Enum):
    SUPPORTED = "SUPPORTED"
    CAUTION = "CAUTION"
    ABSTAIN = "ABSTAIN"
    SYSTEM_ERROR = "SYSTEM_ERROR"


class AbstentionReasonCode(str, Enum):
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    SAFETY_CONTRAINDICATION = "SAFETY_CONTRAINDICATION"
    MULTIMODAL_DISCORDANCE = "MULTIMODAL_DISCORDANCE"
    GOVERNANCE_POLICY = "GOVERNANCE_POLICY"


@dataclass
class GovernanceDecisionRecord:
    status: GovernanceStatus
    abstention_code: Optional[AbstentionReasonCode] = None
    calibrated_confidence: float = 0.85
    reasons: List[str] = field(default_factory=list)
    blocking_findings: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)
    evidence_sufficiency: str = "SUFFICIENT"
    safety_assessment: Dict[str, Any] = field(default_factory=dict)
    discordance_score: float = 0.0
    provenance_refs: List[str] = field(default_factory=list)
    evaluated_agents: List[str] = field(default_factory=list)
    required_actions: List[str] = field(default_factory=list)
    clinician_review_required: bool = True
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    decision_hash: str = ""

    def __post_init__(self):
        if not self.decision_hash:
            payload = (
                f"{self.status.value}|{self.abstention_code.value if self.abstention_code else 'NONE'}|"
                f"{self.calibrated_confidence:.4f}|{sorted(self.reasons)}|{self.discordance_score:.4f}|{self.timestamp}"
            )
            self.decision_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_status": self.status.value,
            "abstention_code": self.abstention_code.value if self.abstention_code else None,
            "confidence": self.calibrated_confidence,
            "is_abstaining": self.status == GovernanceStatus.ABSTAIN,
            "reasons": self.reasons,
            "blocking_findings": self.blocking_findings,
            "warnings": self.warnings,
            "evidence_sufficiency": self.evidence_sufficiency,
            "safety_assessment": self.safety_assessment,
            "discordance_score": self.discordance_score,
            "provenance_refs": self.provenance_refs,
            "evaluated_agents": self.evaluated_agents,
            "required_actions": self.required_actions,
            "clinician_review_required": self.clinician_review_required,
            "timestamp": self.timestamp,
            "provenance_hash": self.decision_hash
        }
