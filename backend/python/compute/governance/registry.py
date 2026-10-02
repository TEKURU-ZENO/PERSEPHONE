"""
Governance Registry Module for PERSEPHONE Governance Platform.
Central orchestrator for clinical rules, contraindications, multimodal consistency,
epistemic uncertainty calibration, clinical abstention gating, and cryptographic audit proofs.
"""
from typing import Dict, List, Any, Optional
import time

from backend.python.compute.governance.safety.clinical_rules import ClinicalRulesEvaluator
from backend.python.compute.governance.safety.contraindications import ContraindicationsEvaluator
from backend.python.compute.governance.safety.escalation import EscalationProtocol
from backend.python.compute.governance.validation.factuality import FactualityVerifier
from backend.python.compute.governance.validation.consistency import ConsistencyAuditor
from backend.python.compute.governance.validation.calibration import CalibrationEngine
from backend.python.compute.governance.validation.drift import DriftDetector
from backend.python.compute.governance.uncertainty.confidence import UncertaintyDecomposer
from backend.python.compute.governance.uncertainty.abstention import ClinicalAbstentionEngine
from backend.python.compute.governance.provenance.audit import GovernanceAuditLogger
from backend.python.compute.governance.provenance.lineage import GovernanceLineageTracker
from backend.python.compute.governance.monitoring.model_drift import ModelDriftMonitor
from backend.python.compute.governance.monitoring.performance import GovernancePerformanceTracker
from backend.python.compute.governance.decision import GovernanceDecision


class GovernanceRegistry:
    """
    Authoritative Governance Orchestrator enforcing deterministic safety checks
    and immutable GovernanceDecision issuance.
    """

    @classmethod
    def evaluate_safety(
        cls,
        patient_data: Dict[str, Any],
        proposed_drug: str = "Olaparib"
    ) -> Dict[str, Any]:
        start = time.perf_counter()
        patient_metrics = patient_data.get("clinicalMetrics") or patient_data.get("labs") or patient_data

        rules_res = ClinicalRulesEvaluator.evaluate_organ_clearances(patient_metrics, proposed_drug)
        contra_res = ContraindicationsEvaluator.evaluate_contraindications(patient_data, proposed_drug)
        escalation_res = EscalationProtocol.synthesize_escalation(
            rules_res.get("violations", []),
            contra_res.get("contraindications", []),
            patient_id=str(patient_data.get("id", "patient-a"))
        )
        elapsed = round((time.perf_counter() - start) * 1000, 2)

        return {
            "patient_id": patient_data.get("id", "patient-a"),
            "proposed_drug": proposed_drug,
            "clinical_rules": rules_res,
            "contraindications": contra_res,
            "escalation": escalation_res,
            "cleared_for_therapy": rules_res["passed_safety_thresholds"] and contra_res["cleared_for_therapy"],
            "processingTimeMs": elapsed
        }

    @classmethod
    def validate_consistency(
        cls,
        patient_data: Dict[str, Any],
        imaging_signals: Optional[Dict[str, Any]] = None,
        monitoring_signals: Optional[Dict[str, Any]] = None,
        claims: Optional[List[Dict[str, Any]]] = None,
        proposed_drug: str = "Olaparib"
    ) -> Dict[str, Any]:
        start = time.perf_counter()
        imaging_signals = imaging_signals or {}
        monitoring_signals = monitoring_signals or {}
        claims = claims or []

        consistency_res = ConsistencyAuditor.evaluate_multimodal_consistency(
            patient_data, imaging_signals, monitoring_signals, proposed_drug
        )
        factuality_res = FactualityVerifier.verify_factuality(claims)
        calib_res = CalibrationEngine.evaluate_calibration([], [])

        # Feature drift check
        features_to_check = {
            "baseline_tumor_volume": float(imaging_signals.get("baseline_volume", 82.0)),
            "carrying_capacity_K": float(patient_data.get("carrying_capacity", 205.0)),
            "resistant_fraction": float(patient_data.get("resistant_fraction", 0.05)),
            "tmb_score": float(patient_data.get("tmb_score", 7.0)),
            "hrd_score": float(patient_data.get("hrd_score", 58.0))
        }
        drift_res = DriftDetector.evaluate_feature_drift(features_to_check)
        elapsed = round((time.perf_counter() - start) * 1000, 2)

        return {
            "patient_id": patient_data.get("id", "patient-a"),
            "consistency": consistency_res,
            "factuality": factuality_res,
            "calibration": calib_res,
            "drift": drift_res,
            "is_valid": consistency_res["is_concordant"] and factuality_res["passed_factuality"] and drift_res["safe_for_inference"],
            "processingTimeMs": elapsed
        }

    @classmethod
    def evaluate_abstention(
        cls,
        patient_data: Dict[str, Any],
        proposed_drug: str = "Olaparib",
        imaging_signals: Optional[Dict[str, Any]] = None,
        monitoring_signals: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        start = time.perf_counter()
        safety_eval = cls.evaluate_safety(patient_data, proposed_drug)
        consistency_eval = cls.validate_consistency(patient_data, imaging_signals, monitoring_signals, proposed_drug=proposed_drug)

        evidence_count = int(patient_data.get("evidence_count", 3))
        multimodal_disc = float(consistency_eval["consistency"]["discordance_index"])
        drift_psi = float(max([f.get("psi", 0.0) for f in consistency_eval["drift"]["drifted_features"]] or [0.05]))

        uncertainty_profile = UncertaintyDecomposer.decompose_uncertainty(
            evidence_count=evidence_count,
            multimodal_discordance=multimodal_disc,
            drift_psi=drift_psi
        )

        abstention_res = ClinicalAbstentionEngine.evaluate_decision(
            patient_data=patient_data,
            safety_audit=safety_eval["clinical_rules"],
            consistency_audit=consistency_eval["consistency"],
            uncertainty_profile=uncertainty_profile
        )
        elapsed = round((time.perf_counter() - start) * 1000, 2)
        abstention_res["processingTimeMs"] = elapsed
        return abstention_res

    @classmethod
    def audit_governance(
        cls,
        patient_id: str,
        decision_verdict: Dict[str, Any],
        safety_findings: Optional[Dict[str, Any]] = None,
        validation_findings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        start = time.perf_counter()
        safety_findings = safety_findings or {}
        validation_findings = validation_findings or {}

        cert = GovernanceAuditLogger.generate_audit_certificate(
            patient_id=patient_id,
            decision_status=decision_verdict.get("decision_status", "APPROVED"),
            safety_status=safety_findings.get("status", "PASSED"),
            abstention_code=decision_verdict.get("abstention_code"),
            calibrated_confidence=decision_verdict.get("confidence", 0.85),
            rule_versions=safety_findings.get("rule_versions_applied", ["STD-RENAL-2024.1", "STD-HEM-2024.1"])
        )

        lineage = GovernanceLineageTracker.trace_governance_lineage(
            patient_id=patient_id,
            safety_findings=safety_findings,
            validation_findings=validation_findings,
            decision_verdict=decision_verdict
        )
        elapsed = round((time.perf_counter() - start) * 1000, 2)

        return {
            "certificate": cert,
            "lineage": lineage,
            "processingTimeMs": elapsed
        }

    @classmethod
    def run_full_governance_pipeline(
        cls,
        payload: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executes the entire deterministic governance workflow and produces an immutable GovernanceDecision.
        """
        start = time.perf_counter()
        data = payload or {}
        patient_data = data.get("patient") or data.get("patient_data") or {
            "id": data.get("patientId", "patient-a"),
            "diagnosis": "High-Grade Serous Ovarian Cancer",
            "stage": "Stage IIIc",
            "variants": ["BRCA1 185delAG"],
            "hrd_score": 62.0
        }
        proposed_drug = str(data.get("drug") or data.get("proposed_drug", "Olaparib"))
        imaging_signals = data.get("imaging") or data.get("imaging_signals") or {}
        monitoring_signals = data.get("monitoring") or data.get("monitoring_signals") or {}
        claims = data.get("claims") or []

        # 1. Safety & organ rules
        safety_eval = cls.evaluate_safety(patient_data, proposed_drug)

        # 2. Multimodal validation & drift
        validation_eval = cls.validate_consistency(patient_data, imaging_signals, monitoring_signals, claims, proposed_drug)

        # 3. Uncertainty & Abstention Gating
        evidence_count = len(claims) if claims else int(patient_data.get("evidence_count", 3))
        multimodal_disc = float(validation_eval["consistency"]["discordance_index"])
        drift_psi = float(max([f.get("psi", 0.0) for f in validation_eval["drift"]["drifted_features"]] or [0.04]))

        uncertainty_profile = UncertaintyDecomposer.decompose_uncertainty(
            evidence_count=evidence_count,
            multimodal_discordance=multimodal_disc,
            drift_psi=drift_psi
        )

        abstention_eval = ClinicalAbstentionEngine.evaluate_decision(
            patient_data=patient_data,
            safety_audit=safety_eval["clinical_rules"],
            consistency_audit=validation_eval["consistency"],
            uncertainty_profile=uncertainty_profile
        )

        # 4. Construct Immutable GovernanceDecision Object
        rule_versions = list(safety_eval["clinical_rules"].get("rule_versions_applied", [])) + [abstention_eval.get("policy_version", "POL-ABSTAIN-2026.1")]
        model_versions = ["governance-engine-v19", "calibration-v2", "consistency-v1"]
        evidence_refs = [f"PMID:{c.get('pmid', '30345884')}" for c in claims if c.get("pmid")] or ["PMID:30345884 (SOLO-1)", "NCCN-OV-v1.2026"]

        decision_obj = GovernanceDecision(
            decision_status=abstention_eval["decision_status"],
            confidence=abstention_eval["confidence"],
            abstention_code=abstention_eval["abstention_code"],
            reason=abstention_eval["reason"],
            safety_findings=safety_eval["clinical_rules"].get("violations", []),
            validation_findings=validation_eval["factuality"].get("violations", []),
            contradiction_findings=validation_eval["consistency"].get("discordance_flags", []),
            uncertainty=uncertainty_profile,
            drift_status=validation_eval["drift"]["drift_status"],
            evidence_refs=evidence_refs,
            rule_versions=rule_versions,
            model_versions=model_versions,
            required_actions=abstention_eval["required_actions"],
            clinician_guidance=abstention_eval["clinician_guidance"]
        )

        # 5. Audit Certificate & Lineage
        audit_res = cls.audit_governance(
            patient_id=str(patient_data.get("id", "patient-a")),
            decision_verdict=decision_obj.to_dict(),
            safety_findings=safety_eval["clinical_rules"],
            validation_findings=validation_eval["consistency"]
        )

        # 6. Record in ModelDriftMonitor
        ModelDriftMonitor.record_inference(
            patient_id=str(patient_data.get("id", "patient-a")),
            decision_status=decision_obj.decision_status,
            calibrated_confidence=decision_obj.confidence,
            discordance_index=multimodal_disc,
            drift_psi=drift_psi
        )

        elapsed = round((time.perf_counter() - start) * 1000, 2)

        return {
            "decision": decision_obj.to_dict(),
            "safety": safety_eval,
            "validation": validation_eval,
            "uncertainty": uncertainty_profile,
            "abstention": abstention_eval,
            "audit": audit_res,
            "telemetry": ModelDriftMonitor.get_drift_telemetry(),
            "performance": GovernancePerformanceTracker.get_performance_metrics(),
            "processingTimeMs": elapsed
        }
