"""
Guideline Recommender module for PERSEPHONE Research Intelligence Platform.
Matches patient profiles against versioned oncology guidelines (NCCN, ASCO, ESMO).
"""
from typing import Dict, List, Any, Optional
from backend.python.compute.research_intelligence.guidelines.sources import ALL_GUIDELINE_RULES
from backend.python.compute.research_intelligence.guidelines.parser import GuidelineParser
from backend.python.compute.research_intelligence.guidelines.temporal import TemporalValidityEngine


class GuidelineRecommender:
    """
    Coordinates guideline rule matching, temporal validation, and preference categorization.
    """

    @classmethod
    def evaluate_patient_guidelines(
        cls,
        patient_data: Dict[str, Any],
        proposed_drug: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Evaluates all authoritative guideline sources (NCCN, ASCO, ESMO) for the patient.
        """
        matched_recommendations = []

        for rule in ALL_GUIDELINE_RULES:
            if proposed_drug and proposed_drug.upper() not in rule.recommended_drug.upper():
                continue

            eval_res = GuidelineParser.evaluate_rule(rule, patient_data)
            if eval_res["eligible"]:
                ref = rule.reference
                temp_status = TemporalValidityEngine.evaluate_temporal_validity(
                    effective_from=ref.effective_from,
                    effective_until=ref.effective_until,
                    superseded_by=ref.superseded_by
                )

                matched_recommendations.append({
                    "rule_id": rule.rule_id,
                    "organization": ref.organization,
                    "guideline_title": ref.guideline_title,
                    "version": ref.version,
                    "section": ref.section,
                    "recommended_drug": rule.recommended_drug,
                    "treatment_line": rule.treatment_line,
                    "evidence_category": ref.evidence_category,
                    "preference_tier": ref.preference_tier,
                    "rationale": rule.rationale,
                    "source_url": ref.source_url,
                    "temporal_validity": temp_status,
                    "matched_criteria": eval_res["biomarker_matches"]
                })

        # Sort: Category 1 first, then Category 2A; Preferred first
        def sort_key(rec):
            cat_rank = 1 if "1" in rec["evidence_category"] else (2 if "2A" in rec["evidence_category"] else 3)
            pref_rank = 1 if rec["preference_tier"] == "Preferred" else 2
            return (cat_rank, pref_rank)

        matched_recommendations.sort(key=sort_key)
        return matched_recommendations
