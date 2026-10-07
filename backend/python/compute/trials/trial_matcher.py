"""
Trial Matcher module for PERSEPHONE Clinical Trials Intelligence.
Computes multi-dimensional matching scores between patient clinical profiles
and trial protocol requirements.
"""
from backend.python.compute.trials.eligibility_extractor import EligibilityExtractor

class TrialMatcher:
    """
    Evaluates patient eligibility and computes affinity scores across clinical trials.
    """

    @classmethod
    def match_patient_to_trials(cls, patient_profile, trial_list):
        """
        Matches a patient profile against an iterable of trial records.
        """
        results = []
        p_stage = (patient_profile.get("stage") or "").lower()

        for trial in trial_list:
            criteria = EligibilityExtractor.extract_criteria(
                trial.get("enrollmentCriteria", ""),
                trial=trial
            )
            eval_res = EligibilityExtractor.evaluate_eligibility(patient_profile, criteria)

            disqualified = (eval_res["eligibility"] == "ineligible")
            biomarker_match = eval_res["biomarker_match"]

            # 1. Genomic Score (0 to 1)
            genomic_score = 1.0 if biomarker_match else 0.0

            # 2. Condition / Indication Score (0 to 1)
            has_cancer_mismatch = any("Cancer type mismatch" in v for v in eval_res["violations"])
            cond_score = 0.0 if has_cancer_mismatch else 1.0

            # 3. Stage Score (0 to 1)
            t_stages = [s.lower() for s in criteria.get("stages", [])]
            stage_score = 1.0 if (p_stage and any(p_stage in s or s in p_stage for s in t_stages)) else 0.4

            # 4. Performance Score (0 to 1)
            perf_score = 1.0 if not disqualified else 0.0

            if disqualified:
                match_score = 0.0
                match_type = "disqualified"
            else:
                base_score = (
                    genomic_score * 0.40 +
                    cond_score * 0.30 +
                    stage_score * 0.15 +
                    perf_score * 0.15
                )
                if eval_res["eligibility"] == "possibly eligible":
                    match_score = round(base_score * 0.85, 3)
                else:
                    match_score = round(base_score, 3)
                match_type = eval_res["eligibility"]

            results.append({
                "trialId": trial.get("trialId"),
                "title": trial.get("title"),
                "phase": trial.get("phase", "Phase II"),
                "status": trial.get("status", "Active"),
                "recruitment_status": eval_res["recruitment_status"],
                "eligibility": eval_res["eligibility"],
                "enrollment": eval_res["enrollment"],
                "status_label": eval_res["status_label"],
                "biomarker_match": biomarker_match,
                "disqualified": disqualified,
                "cancer_types": trial.get("cancer_types", []),
                "conditions": trial.get("conditions", []),
                "drugs": trial.get("drugs", []),
                "biomarkers": trial.get("biomarkers", []),
                "sponsor": trial.get("sponsor", ""),
                "locations": trial.get("locations", []),
                "last_verified": trial.get("last_verified"),
                "verification_date": trial.get("last_verified"),
                "matchScore": match_score,
                "matchType": match_type,
                "isEligible": eval_res["is_eligible"],
                "matchedCriteria": eval_res["matched_criteria"],
                "unmatchedCriteria": eval_res["unmatched_criteria"],
                "matched_criteria": eval_res["matched_criteria"],
                "unmatched_criteria": eval_res["unmatched_criteria"],
                "violations": eval_res["violations"]
            })

        return results
