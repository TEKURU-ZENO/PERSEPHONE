"""
Clinical Escalation Module for PERSEPHONE Governance Platform.
Defines formalized clinical escalation protocols, severity triage, and required actions
when safety boundaries or contraindications are breached.
"""
from typing import Dict, List, Any, Optional
import time


class EscalationProtocol:
    """
    Triage and escalation manager for clinical safety violations.
    """
    SEVERITY_LEVELS = ["INFORMATIONAL", "MODERATE", "SEVERE", "CRITICAL"]

    @classmethod
    def synthesize_escalation(
        cls,
        clinical_rule_violations: List[Dict[str, Any]],
        contraindications: List[Dict[str, Any]],
        patient_id: str = "patient-a"
    ) -> Dict[str, Any]:
        triggers = []

        # Process clinical rule violations
        for v in clinical_rule_violations:
            sev = v.get("severity", "SEVERE")
            triggers.append({
                "trigger_id": f"ESC-RULE-{v.get('organ_system', 'GEN')}",
                "source": "CLINICAL_ORGAN_RULES",
                "severity": sev,
                "metric": v.get("metric"),
                "observed_value": v.get("observed_value"),
                "action": v.get("action"),
                "rationale": v.get("rationale"),
                "required_escalation": cls._determine_required_escalation(sev, v.get("action"))
            })

        # Process contraindications
        for c in contraindications:
            sev = c.get("severity", "CRITICAL")
            triggers.append({
                "trigger_id": f"ESC-CONTRA-{c.get('rule_id', 'GEN')}",
                "source": "CONTRAINDICATION_REGISTRY",
                "severity": sev,
                "trigger_type": c.get("trigger_type"),
                "action": c.get("action"),
                "rationale": c.get("rationale"),
                "required_escalation": "PERMANENT_THERAPY_CONTRAINDICATION_AND_IMMEDIATE_MD_NOTIFICATION"
            })

        # Determine overall escalation level
        if any(t["severity"] == "CRITICAL" for t in triggers):
            overall_severity = "CRITICAL"
            recommended_disposition = "BLOCK_RECOMMENDATION_ESCALATE_TO_ATTENDING"
            requires_human_override = True
        elif any(t["severity"] == "SEVERE" for t in triggers):
            overall_severity = "SEVERE"
            recommended_disposition = "HOLD_THERAPY_PENDING_LAB_CONFIRMATION"
            requires_human_override = True
        elif any(t["severity"] == "MODERATE" for t in triggers):
            overall_severity = "MODERATE"
            recommended_disposition = "PROCEED_WITH_MANDATED_DOSE_REDUCTION"
            requires_human_override = False
        else:
            overall_severity = "CLEARED"
            recommended_disposition = "CLEARED_FOR_STANDARD_TUMOR_BOARD_CONSIDERATION"
            requires_human_override = False

        return {
            "overall_severity": overall_severity,
            "escalation_triggers_count": len(triggers),
            "triggers": triggers,
            "recommended_disposition": recommended_disposition,
            "requires_human_override": requires_human_override,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }

    @staticmethod
    def _determine_required_escalation(severity: str, action: Optional[str]) -> str:
        if severity == "CRITICAL" or action == "CONTRAINDICATED":
            return "IMMEDIATE_ONCOLOGY_ATTENDING_ESCALATION_AND_TREATMENT_HOLD"
        elif severity == "HIGH" or action == "WITHHOLD_UNTIL_RECOVERY":
            return "WEEKLY_LABORATORY_SURVEILLANCE_AND_DOSE_HOLD"
        elif severity == "MODERATE":
            return "CLINICIAN_REVIEW_AND_DOSE_ADJUSTMENT"
        return "ROUTINE_MONITORING"
