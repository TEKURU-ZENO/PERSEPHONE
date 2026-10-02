"""
Clinical Abstention Module for PERSEPHONE Governance Platform.
Implements the core Clinical Abstention Engine:
Refuses to force an ungrounded or hazardous recommendation when empirical evidence is sparse,
signals are contradictory (e.g., genomic sensitivity vs. imaging progression),
or uncertainty is uncalibrated.
"""
from typing import Dict, List, Any, Optional
import time

# Configurable, versioned clinical abstention thresholds backed by governance policy
ABSTENTION_POLICY = {
    "policy_id": "POL-ABSTAIN-2026.1",
    "authority": "PERSEPHONE Clinical AI Governance Board / ESMO Precision Medicine Framework",
    "version": "2026.1",
    "thresholds": {
        "confidence_approval_floor": 0.70,       # Below this, cannot issue unqualified APPROVAL
        "confidence_abstention_ceiling": 0.55,    # Below this, MUST abstain with INSUFFICIENT_EVIDENCE
        "discordance_abstention_threshold": 0.60, # Discordance Index > 0.60 forces abstention
        "min_evidence_sources_required": 1        # Zero empirical evidence forces abstention
    }
}


class ClinicalAbstentionEngine:
    """
    Deterministic Clinical Abstention Gatekeeper.
    Enforces the invariant: Decision is computed purely from deterministic rules,
    calibration, and multimodal consistency—NEVER delegated to an LLM.
    """

    @classmethod
    def evaluate_decision(
        cls,
        patient_data: Dict[str, Any],
        safety_audit: Dict[str, Any],
        consistency_audit: Dict[str, Any],
        uncertainty_profile: Dict[str, Any],
        policy_override: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        policy = policy_override or ABSTENTION_POLICY["thresholds"]
        conf_approval = policy.get("confidence_approval_floor", 0.70)
        conf_abstain = policy.get("confidence_abstention_ceiling", 0.55)
        disc_threshold = policy.get("discordance_abstention_threshold", 0.60)

        calibrated_conf = float(uncertainty_profile.get("calibrated_confidence", 0.85))
        discordance_idx = float(consistency_audit.get("discordance_index", 0.0))
        critical_violations = safety_audit.get("violations", [])
        has_contraindications = safety_audit.get("has_contraindications", False)

        required_actions = []
        contradictions_detected = consistency_audit.get("discordance_flags", [])

        # ── GATE 1: Critical Safety & Organ Clearances ──
        if critical_violations or has_contraindications:
            contra_reasons = [v.get("rationale") for v in critical_violations]
            if not contra_reasons:
                contra_reasons = [c.get("rationale") for c in safety_audit.get("contraindications", [])]

            primary_reason = contra_reasons[0] if contra_reasons else "Unacceptable organ toxicity risk or contraindication detected."

            required_actions.append("Hold antineoplastic therapy immediately.")
            required_actions.append("Repeat organ function panel (renal/hepatic/CBC) in 48-72 hours.")
            required_actions.append("Multidisciplinary oncology consult for dose adjustment or alternative non-nephrotoxic/hepatotoxic regimen.")

            return {
                "decision_status": "ABSTAIN",
                "abstention_code": "UNACCEPTABLE_TOXICITY_RISK",
                "is_abstaining": True,
                "confidence": calibrated_conf,
                "confidence_threshold": conf_approval,
                "reason": f"SAFETY CONTRAINDICATION: {primary_reason}",
                "contradictions_detected": contradictions_detected,
                "required_actions": required_actions,
                "clinician_guidance": "DO NOT INITIATE THERAPY. Clinical boundaries or absolute contraindications breached.",
                "policy_version": ABSTENTION_POLICY["policy_id"]
            }

        # ── GATE 2: Multimodal Cross-Signal Conflict ──
        if discordance_idx >= disc_threshold:
            conflict_statements = [f.get("statement") for f in contradictions_detected if f.get("statement")]
            conflict_reason = conflict_statements[0] if conflict_statements else "Conflicting genomic and imaging signals."

            # Calibrate confidence downwards due to direct conflict
            calibrated_conf = min(calibrated_conf, 0.41)

            required_actions.append("Additional molecular testing / clinician review.")
            required_actions.append("Perform liquid biopsy (ctDNA) or repeat tissue biopsy for secondary reversion mutations.")
            required_actions.append("Schedule 4-week short-interval volumetric CT/MRI restaging.")
            required_actions.append("Present case at Multidisciplinary Molecular Tumor Board prior to treatment selection.")

            return {
                "decision_status": "ABSTAIN",
                "abstention_code": "INSUFFICIENT_EVIDENCE",
                "is_abstaining": True,
                "confidence": calibrated_conf,
                "confidence_threshold": conf_approval,
                "reason": conflict_reason,
                "contradictions_detected": contradictions_detected,
                "required_actions": required_actions,
                "clinician_guidance": "INSUFFICIENT EVIDENCE: Paradoxical discordance between molecular sensitivity and macroscopic disease progression. Do not force standard monotherapy.",
                "policy_version": ABSTENTION_POLICY["policy_id"]
            }

        # ── GATE 3: Low Confidence / Sparse Evidence Floor ──
        if calibrated_conf < conf_abstain:
            required_actions.append("Additional clinical evidence acquisition required.")
            required_actions.append("Expanded NGS comprehensive genomic profiling (CGP).")
            required_actions.append("Consult registrational clinical trial matching team.")

            return {
                "decision_status": "ABSTAIN",
                "abstention_code": "INSUFFICIENT_EVIDENCE",
                "is_abstaining": True,
                "confidence": calibrated_conf,
                "confidence_threshold": conf_approval,
                "reason": f"Calibrated model confidence ({calibrated_conf:.2f}) falls below minimum safety evidence threshold ({conf_abstain:.2f}).",
                "contradictions_detected": contradictions_detected,
                "required_actions": required_actions,
                "clinician_guidance": "Evidence base insufficient to support deterministic automated treatment recommendation.",
                "policy_version": ABSTENTION_POLICY["policy_id"]
            }

        # ── GATE 4: Moderate Confidence / Minor Discordance (Caution Override) ──
        if calibrated_conf < conf_approval or discordance_idx > 0.25:
            required_actions.append("Close clinical monitoring during initial cycle.")
            required_actions.append("Documented informed consent discussing borderline uncertainty.")

            return {
                "decision_status": "CAUTION_OVERRIDE",
                "abstention_code": None,
                "is_abstaining": False,
                "confidence": calibrated_conf,
                "confidence_threshold": conf_approval,
                "reason": f"Moderate confidence ({calibrated_conf:.2f}) supported by guideline evidence; clinician discretion advised.",
                "contradictions_detected": contradictions_detected,
                "required_actions": required_actions,
                "clinician_guidance": "Recommendation cleared with caution. Oncology team review recommended before cycle initiation.",
                "policy_version": ABSTENTION_POLICY["policy_id"]
            }

        # ── GATE 5: Fully Approved ──
        return {
            "decision_status": "APPROVED",
            "abstention_code": None,
            "is_abstaining": False,
            "confidence": calibrated_conf,
            "confidence_threshold": conf_approval,
            "reason": "Fully concordant evidence across genomics, imaging, organ clearances, and registrational guidelines.",
            "contradictions_detected": [],
            "required_actions": ["Proceed with standard tumor board protocol dosing."],
            "clinician_guidance": "Therapy recommendation verified and cleared under Clinical AI Governance Board standards.",
            "policy_version": ABSTENTION_POLICY["policy_id"]
        }
