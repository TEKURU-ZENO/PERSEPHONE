"""
23rd Council Member: Governance & Clinical Abstention Agent.
Deliberates late in the council cycle (after safety and validation, before explainability and report).
Synthesizes safety audits, validation scorecards, multimodal concordance, and epistemic uncertainty
to issue the definitive, immutable GovernanceDecision.
"""
from typing import Dict, Any, Optional
from backend.python.compute.ai_runtime.agents.instances.base import BaseClinicalAgent
from backend.python.compute.governance.registry import GovernanceRegistry


class GovernanceAgent(BaseClinicalAgent):
    """
    Council Member #23: Governance & Clinical Abstention Agent.
    Enforces deterministic safety boundaries, executes multimodal consistency checks,
    and triggers clinical abstention when evidence is insufficient or contradictory.
    """

    def __init__(self):
        super().__init__("Governance Agent", "Governance")
        self.data_sources = [
            "ClinicalRulesEvaluator (KDIGO/CTCAE)",
            "ContraindicationsEvaluator (CPIC)",
            "ConsistencyAuditor (Multimodal Concordance)",
            "CalibrationEngine (ECE/Brier)",
            "ClinicalAbstentionEngine"
        ]

    def initialize(self, blackboard):
        self.patient = blackboard.read("patient_twin") or {"id": "patient-a"}
        self.safety_audits = blackboard.read("safety_audits") or []
        self.validation_scorecard = blackboard.read("validation_scorecard") or {}
        self.claims = blackboard.read("CLINICAL_CLAIMS") or []
        self.top_drugs = blackboard.read("DRUG_SENSITIVITY_SCORES") or []
        self.proposed_drug = self.top_drugs[0].get("drug", "Olaparib") if self.top_drugs else "Olaparib"

        # Read multimodal signals
        self.imaging_signals = {
            "recist_status": blackboard.read("RECIST_STATUS") or "PR",
            "volume_delta_pct": blackboard.read("VOLUME_DELTA_PCT") or -25.0,
            "necrotic_fraction": blackboard.read("NECROSIS") or 0.15
        }
        self.monitoring_signals = {
            "current_velocity": (blackboard.read("LONGITUDINAL_STATE") or {}).get("trajectory", {}).get("currentVelocity", 0.0)
        }

    def plan(self, blackboard):
        pass

    def execute(self, blackboard):
        payload = {
            "patient": self.patient,
            "drug": self.proposed_drug,
            "imaging": self.imaging_signals,
            "monitoring": self.monitoring_signals,
            "claims": self.claims
        }
        self.governance_result = GovernanceRegistry.run_full_governance_pipeline(payload)
        self.decision = self.governance_result["decision"]
        self.confidence = float(self.decision.get("confidence", 0.85))

    def reflect(self, blackboard):
        pass

    def publish(self, blackboard):
        # Publish immutable governance decision and audit certificates
        blackboard.write("GOVERNANCE_DECISION", self.decision)
        blackboard.write("GOVERNANCE_AUDIT", self.governance_result.get("audit", {}))

        if self.decision.get("decision_status") == "ABSTAIN":
            abstention_data = {
                "is_abstaining": True,
                "code": self.decision.get("abstention_code", "INSUFFICIENT_EVIDENCE"),
                "reason": self.decision.get("reason"),
                "confidence": self.confidence,
                "required_actions": self.decision.get("required_actions", [])
            }
            blackboard.write("CLINICAL_ABSTENTION", abstention_data)

        blackboard.add_contribution(self.name, self.decision)
