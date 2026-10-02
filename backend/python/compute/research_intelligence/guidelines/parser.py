"""
Guideline Decision Rule Parser for PERSEPHONE Research Intelligence Platform.
Evaluates patient stage, histology, and biomarker profiles against versioned decision rules.
"""
from typing import Dict, List, Any, Optional
from backend.python.compute.research_intelligence.guidelines.schemas import DecisionRule


class GuidelineParser:
    """
    Evaluates patient eligibility against versioned guideline decision rules.
    """

    @classmethod
    def evaluate_rule(cls, rule: DecisionRule, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determines if patient matches the decision rule's disease, stage, and biomarker criteria.
        """
        patient_disease = str(patient_data.get("diagnosis", "")).upper()
        patient_stage = str(patient_data.get("stage", "")).upper()
        variants = [str(v).upper() for v in (patient_data.get("variants") or [])]
        hrd_score = float(patient_data.get("hrd_score", 52.0 if any("BRCA" in v for v in variants) else 20.0))

        # 1. Disease check
        disease_match = (rule.disease.upper() in patient_disease) or (patient_disease in rule.disease.upper())

        # 2. Stage check
        stage_match = False
        if not rule.stage:
            stage_match = True
        else:
            for s in rule.stage:
                if s.upper() in patient_stage or patient_stage in s.upper():
                    stage_match = True
                    break

        # 3. Biomarker checks
        biomarker_matches = []
        biomarker_mismatches = []

        for gene, req in rule.biomarker_requirements.items():
            gene_up = gene.upper()
            if gene_up == "HRD":
                if req == "positive" and (hrd_score >= 42.0 or any("BRCA" in v for v in variants)):
                    biomarker_matches.append(f"HRD Score {hrd_score} >= 42 (Positive)")
                elif req == "negative" and hrd_score < 42.0:
                    biomarker_matches.append(f"HRD Score {hrd_score} < 42 (Negative)")
                else:
                    biomarker_mismatches.append(f"HRD status mismatch: patient score={hrd_score}, requires {req}")
            else:
                has_mut = any(gene_up in v for v in variants)
                if req == "mutated" and has_mut:
                    biomarker_matches.append(f"{gene_up} mutated")
                elif req == "wildtype" and not has_mut:
                    biomarker_matches.append(f"{gene_up} wildtype")
                else:
                    biomarker_mismatches.append(f"Requires {gene_up} {req}")

        eligible = disease_match and stage_match and (len(biomarker_mismatches) == 0)

        return {
            "rule_id": rule.rule_id,
            "eligible": eligible,
            "disease_match": disease_match,
            "stage_match": stage_match,
            "biomarker_matches": biomarker_matches,
            "biomarker_mismatches": biomarker_mismatches
        }
