"""
Unit tests for PERSEPHONE Phase 19: Clinical Safety, Governance & Validation Platform.
Covers:
- ClinicalRulesEvaluator (KDIGO 2024, CTCAE v5.0, ICH E14)
- ContraindicationsEvaluator (CPIC, FDA Boxed Warnings)
- EscalationProtocol (Triage levels & dispositions)
- FactualityVerifier (Grounding & metric inversion checks)
- ConsistencyAuditor (Multimodal Discordance Index)
- CalibrationEngine (ECE, Brier score, temperature scaling)
- DriftDetector (PSI & z-score drift detection)
- GovernanceAuditLogger & GovernanceLineageTracker (SHA-256 certificate & Merkle root)
- ClinicalAbstentionEngine (Deterministic gating)
- GovernanceDecision (Tamper-evident immutability & cryptographic provenance)
- GovernanceRegistry (End-to-end pipeline)
"""

import unittest
from backend.python.compute.governance.safety.clinical_rules import ClinicalRulesEvaluator, ORGAN_RULE_STANDARDS
from backend.python.compute.governance.safety.contraindications import ContraindicationsEvaluator
from backend.python.compute.governance.safety.escalation import EscalationProtocol
from backend.python.compute.governance.validation.factuality import FactualityVerifier
from backend.python.compute.governance.validation.consistency import ConsistencyAuditor
from backend.python.compute.governance.validation.calibration import CalibrationEngine
from backend.python.compute.governance.validation.drift import DriftDetector
from backend.python.compute.governance.provenance.audit import GovernanceAuditLogger
from backend.python.compute.governance.provenance.lineage import GovernanceLineageTracker
from backend.python.compute.governance.uncertainty.abstention import ClinicalAbstentionEngine
from backend.python.compute.governance.uncertainty.confidence import UncertaintyDecomposer
from backend.python.compute.governance.decision import GovernanceDecision
from backend.python.compute.governance.registry import GovernanceRegistry


class TestClinicalGovernancePlatform(unittest.TestCase):

    def setUp(self):
        self.patient_normal = {
            "id": "patient-normal",
            "name": "Elena Rostova",
            "cancer_type": "High-Grade Serous Ovarian Carcinoma",
            "variants": ["BRCA1 c.5266dupC"],
            "labs": {
                "eGFR": 75.0,
                "AST_ALT_xULN": 1.0,
                "bilirubin_xULN": 0.8,
                "ANC": 2400,
                "platelets": 210000,
                "QTc": 420
            }
        }
        self.patient_impaired = {
            "id": "patient-impaired",
            "name": "Renal Impairment Subject",
            "cancer_type": "Ovarian",
            "variants": ["BRCA1 c.5266dupC"],
            "labs": {
                "eGFR": 22.0,  # Below KDIGO Stage G4/G5 threshold (<30)
                "AST_ALT_xULN": 6.5,  # Elevated transaminases (> 5x ULN)
                "bilirubin_xULN": 3.2,
                "ANC": 650,    # Critical neutropenia (<1000)
                "platelets": 42000,  # Thrombocytopenia (<50k)
                "QTc": 515     # Critical prolonged QTc (>500ms)
            }
        }

    # 1. Clinical Rules Evaluation (KDIGO / CTCAE / ICH E14)
    def test_clinical_rules_normal_patient(self):
        res = ClinicalRulesEvaluator.evaluate_organ_clearances(self.patient_normal["labs"], "Olaparib")
        self.assertEqual(res["status"], "PASSED")
        self.assertTrue(res["passed_safety_thresholds"])
        self.assertEqual(len(res["violations"]), 0)
        self.assertIn("STD-RENAL-2024.1:v2024.1", res["rule_versions_applied"])

    def test_clinical_rules_impaired_patient(self):
        res = ClinicalRulesEvaluator.evaluate_organ_clearances(self.patient_impaired["labs"], "Olaparib")
        self.assertEqual(res["status"], "FAILED")
        self.assertFalse(res["passed_safety_thresholds"])
        self.assertGreaterEqual(res["critical_violations_count"], 3)
        organs_breached = [v["organ_system"] for v in res["violations"]]
        self.assertIn("RENAL", organs_breached)
        self.assertIn("CARDIAC", organs_breached)

    # 2. Contraindications Evaluator (CPIC / FDA)
    def test_contraindications_evaluator_dpyd_5fu(self):
        patient_dpyd = {
            "id": "patient-dpyd",
            "variants": ["DPYD *2A (c.1905+1G>A)"],
            "cancer_type": "Colorectal"
        }
        res = ContraindicationsEvaluator.evaluate_contraindications(patient_dpyd, "5-FU")
        self.assertEqual(res["status"], "CONTRAINDICATED")
        self.assertTrue(res["has_contraindications"])
        self.assertEqual(res["contraindications"][0]["authority"], "CPIC Guideline for Fluoropyrimidines and DPYD (2023 Update)")
        self.assertEqual(res["contraindications"][0]["severity"], "CRITICAL")

    def test_contraindications_evaluator_clean_patient(self):
        res = ContraindicationsEvaluator.evaluate_contraindications(self.patient_normal, "Olaparib")
        self.assertEqual(res["status"], "CLEARED")
        self.assertFalse(res["has_contraindications"])
        self.assertEqual(len(res["contraindications"]), 0)

    # 3. Escalation Protocol
    def test_escalation_protocol_triage(self):
        breach = [{
            "organ_system": "RENAL",
            "severity": "CRITICAL",
            "metric": "eGFR",
            "observed_value": 22.0,
            "action": "CONTRAINDICATED",
            "rationale": "Severe renal impairment"
        }]
        esc = EscalationProtocol.synthesize_escalation(
            clinical_rule_violations=breach,
            contraindications=[],
            patient_id="patient-test"
        )
        self.assertEqual(esc["overall_severity"], "CRITICAL")
        self.assertTrue(esc["requires_human_override"])
        self.assertEqual(esc["recommended_disposition"], "BLOCK_RECOMMENDATION_ESCALATE_TO_ATTENDING")

    # 4. Factuality Verifier
    def test_factuality_verifier_grounded_claims(self):
        claims = [
            {"claim_id": "CLM-001", "statement": "Olaparib maintains PFS benefit in BRCA1 mutation", "grounding_status": "GROUNDED", "hazard_ratio": 0.62}
        ]
        res = FactualityVerifier.verify_factuality(claims)
        self.assertTrue(res["passed_factuality"])
        self.assertEqual(res["factual_violations_count"], 0)

    def test_factuality_verifier_inverted_metric(self):
        claims = [
            {"claim_id": "CLM-002", "statement": "Drug provides superior survival benefit", "hazard_ratio": 1.45}
        ]
        res = FactualityVerifier.verify_factuality(claims)
        self.assertFalse(res["passed_factuality"])
        self.assertGreater(res["factual_violations_count"], 0)

    # 5. Multimodal Consistency Auditor & Discordance Index
    def test_multimodal_consistency_concordant(self):
        imaging = {"recist_status": "PR", "volume_delta_pct": -28.0, "necrotic_fraction": 0.15}
        monitoring = {"current_velocity": -0.06}
        res = ConsistencyAuditor.evaluate_multimodal_consistency(self.patient_normal, imaging, monitoring, proposed_drug="Olaparib")
        self.assertTrue(res["is_concordant"])
        self.assertLess(res["discordance_index"], 0.40)
        self.assertEqual(res["recommendation"], "PROCEED")

    def test_multimodal_consistency_discordant(self):
        # Patient has sensitive BRCA1, but tumor expanded +35% and velocity is positive
        imaging = {"recist_status": "PD", "volume_delta_pct": 35.0, "necrotic_fraction": 0.15}
        monitoring = {"current_velocity": 0.60}
        res = ConsistencyAuditor.evaluate_multimodal_consistency(self.patient_normal, imaging, monitoring, proposed_drug="Olaparib")
        self.assertFalse(res["is_concordant"])
        self.assertGreaterEqual(res["discordance_index"], 0.40)
        self.assertEqual(res["recommendation"], "TRIGGER_CLINICAL_ABSTENTION_AND_REBIOPSY")

    # 6. Calibration Engine
    def test_calibration_ece_and_brier(self):
        y_prob = [0.9, 0.85, 0.2, 0.75, 0.3, 0.8, 0.15, 0.25, 0.7, 0.1]
        y_true = [1, 1, 0, 1, 0, 1, 0, 0, 1, 0]
        calib = CalibrationEngine.evaluate_calibration(y_prob, y_true, num_bins=5)
        self.assertLessEqual(calib["expected_calibration_error"], 0.25)
        self.assertLess(calib["brier_score"], 0.15)
        self.assertIn(calib["status"], ["WELL_CALIBRATED", "MODERATELY_CALIBRATED", "MISCALIBRATED"])

    # 7. Drift Detection (Feature Drift)
    def test_feature_drift(self):
        features_stable = {
            "baseline_tumor_volume": 82.0,
            "carrying_capacity_K": 205.0,
            "resistant_fraction": 0.05,
            "tmb_score": 7.0,
            "hrd_score": 58.0
        }
        drift = DriftDetector.evaluate_feature_drift(features_stable)
        self.assertEqual(drift["drift_status"], "IN_DISTRIBUTION")
        self.assertTrue(drift["safe_for_inference"])
        self.assertFalse(drift["has_drift"])

    # 8. Clinical Abstention Engine (Deterministic Invariant)
    def test_abstention_engine_approves_concordant_patient(self):
        imaging = {"recist_status": "PR", "volume_delta_pct": -25.0}
        monitoring = {"current_velocity": -0.05}
        dec = GovernanceRegistry.evaluate_abstention(self.patient_normal, "Olaparib", imaging, monitoring)
        self.assertEqual(dec["decision_status"], "APPROVED")
        self.assertGreaterEqual(dec["confidence"], 0.70)
        self.assertFalse(dec["is_abstaining"])

    def test_abstention_engine_abstains_on_discordant_signals(self):
        imaging = {"recist_status": "PD", "volume_delta_pct": 35.0}
        monitoring = {"current_velocity": 0.60}
        dec = GovernanceRegistry.evaluate_abstention(self.patient_normal, "Olaparib", imaging, monitoring)
        self.assertEqual(dec["decision_status"], "ABSTAIN")
        self.assertTrue(dec["is_abstaining"])
        self.assertEqual(dec["abstention_code"], "INSUFFICIENT_EVIDENCE")
        self.assertLess(dec["confidence"], 0.70)
        self.assertGreater(len(dec["required_actions"]), 0)

    def test_abstention_engine_abstains_on_severe_organ_breach(self):
        imaging = {"recist_status": "PR", "volume_delta_pct": -20.0}
        monitoring = {"current_velocity": -0.04}
        dec = GovernanceRegistry.evaluate_abstention(self.patient_impaired, "Olaparib", imaging, monitoring)
        self.assertIn(dec["decision_status"], ["ABSTAIN", "CONTRAINDICATED"])
        self.assertTrue(dec["is_abstaining"])
        self.assertGreater(len(dec["required_actions"]), 0)

    # 9. Immutable GovernanceDecision Object
    def test_governance_decision_immutability(self):
        gov = GovernanceDecision(
            decision_status="APPROVED",
            confidence=0.88,
            abstention_code=None,
            reason="All boundaries cleared.",
            safety_findings=[],
            validation_findings=[],
            contradiction_findings=[],
            uncertainty={"calibrated_confidence": 0.88},
            drift_status="IN_DISTRIBUTION",
            evidence_refs=["PMID:30345884"],
            rule_versions=["STD-RENAL-2024.1:v2024.1"],
            model_versions=["governance-engine-v19"],
            required_actions=["Proceed with dosing"],
            clinician_guidance="Standard monitoring"
        )
        self.assertEqual(gov.decision_status, "APPROVED")
        self.assertEqual(gov.confidence, 0.88)
        self.assertEqual(len(gov.provenance_hash), 64)
        # Attempting to mutate must raise AttributeError
        with self.assertRaises(AttributeError):
            gov.decision_status = "MUTATED"

    # 10. Audit Logger and Lineage Tracker
    def test_audit_certificate_and_merkle_lineage(self):
        cert = GovernanceAuditLogger.generate_audit_certificate(
            patient_id="patient-a",
            decision_status="APPROVED",
            safety_status="PASSED",
            abstention_code=None,
            calibrated_confidence=0.88,
            rule_versions=["STD-RENAL-2024.1", "STD-CTCAE-v5.0"]
        )
        self.assertTrue(cert["certificate_id"].startswith("GOV-CERT-"))
        self.assertEqual(len(cert["certificate_hash"]), 64)  # SHA-256

        lineage = GovernanceLineageTracker.trace_governance_lineage(
            patient_id="patient-a",
            safety_findings={"status": "PASSED"},
            validation_findings={"is_valid": True},
            decision_verdict={"decision_status": "APPROVED"}
        )
        self.assertEqual(len(lineage["governance_root_hash"]), 64)
        self.assertEqual(lineage["verification_status"], "CRYPTOGRAPHICALLY_ANCHORED")

    # 11. Full End-to-End Governance Registry Pipeline
    def test_governance_registry_pipeline(self):
        payload = {
            "patient": self.patient_normal,
            "drug": "Olaparib",
            "imaging": {"recist_status": "PR", "volume_delta_pct": -20.0},
            "monitoring": {"current_velocity": -0.04}
        }
        res = GovernanceRegistry.run_full_governance_pipeline(payload)
        self.assertIn("decision", res)
        self.assertIn("safety", res)
        self.assertIn("validation", res)
        self.assertIn("audit", res)
        self.assertEqual(res["decision"]["decision_status"], "APPROVED")
        self.assertIn("provenance_hash", res["decision"])
        self.assertEqual(len(res["decision"]["provenance_hash"]), 64)


if __name__ == '__main__':
    unittest.main()
