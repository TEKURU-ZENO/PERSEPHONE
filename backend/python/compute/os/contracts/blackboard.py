"""
Blackboard Contract Schema v1.0 for PERSEPHONE OS.
Enforces type specifications and key contracts for the shared blackboard memory.
Prevents contract drift across all 23 Council agents and 5 intelligence planes.
"""
from typing import Dict, Any, Optional


class BlackboardKeyContract:
    """
    Authoritative v1.0 specification for keys shared across agents on the Blackboard.
    """
    CONTRACTS = {
        "patient_twin": {"type": dict, "required_fields": ["id"]},
        "TUMOR_PURITY": {"type": (int, float), "min": 0, "max": 100},
        "NECROSIS": {"type": (int, float), "min": 0, "max": 1.0},
        "BIOMARKER_TIER": {"type": str},
        "TMB": {"type": dict, "required_fields": ["tmb_score"]},
        "DRUG_SENSITIVITY_SCORES": {"type": list},
        "TOP_TRIAL": {"type": dict, "required_fields": ["trialId"]},
        "LONGITUDINAL_STATE": {"type": dict},
        "PREDICTED_ORR": {"type": dict, "required_fields": ["value"]},
        "PREDICTED_PFS_DAYS": {"type": dict, "required_fields": ["value"]},
        "COMPOSITE_BIOMARKER_SCORE": {"type": dict, "required_fields": ["value"]},
        "BEST_PERFORMING_SIMULATED_STRATEGY": {"type": dict, "required_fields": ["arm_id"]},
        "CLINICAL_CLAIMS": {"type": list},
        "EVIDENCE_GRAPH": {"type": dict},
        "safety_audits": {"type": list},
        "validation_scorecard": {"type": dict},
        "GOVERNANCE_DECISION": {"type": dict, "required_fields": ["decision_status"]},
        "final_report": {"type": dict}
    }

    @classmethod
    def validate_write(cls, key: str, value: Any) -> bool:
        """Validates that a blackboard write conforms to the schema contract."""
        if key not in cls.CONTRACTS:
            raise KeyError(f"Blackboard Contract v1.0 Violation: Unregistered or unauthorized key '{key}'")

        if value is None:
            if key in ("TOP_TRIAL", "final_report", "validation_scorecard", "explainability_rationale", "GOVERNANCE_DECISION"):
                return True

        spec = cls.CONTRACTS[key]
        expected_type = spec["type"]
        if not isinstance(value, expected_type):
            raise TypeError(
                f"Blackboard Contract v1.0 Violation for key '{key}': "
                f"Expected {expected_type}, received {type(value)}"
            )

        if isinstance(value, dict) and "required_fields" in spec:
            for field in spec["required_fields"]:
                if field not in value:
                    raise KeyError(
                        f"Blackboard Contract v1.0 Violation for key '{key}': "
                        f"Missing required field '{field}'"
                    )

        if isinstance(value, (int, float)):
            if "min" in spec and value < spec["min"]:
                raise ValueError(f"Value for '{key}' ({value}) below minimum {spec['min']}")
            if "max" in spec and value > spec["max"]:
                raise ValueError(f"Value for '{key}' ({value}) above maximum {spec['max']}")

        return True
