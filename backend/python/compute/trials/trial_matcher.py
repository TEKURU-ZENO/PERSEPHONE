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
        p_genes = set([g.upper() for g in patient_profile.get("variants", ["BRCA1"])])
        p_diag = (patient_profile.get("diagnosis") or "").lower()
        p_stage = (patient_profile.get("stage") or "Stage III").lower()

        for trial in trial_list:
            criteria = EligibilityExtractor.extract_criteria(
                trial.get("enrollmentCriteria", ""),
                trial=trial
            )
            eval_res = EligibilityExtractor.evaluate_eligibility(patient_profile, criteria)

            # 1. Genomic Score (0 to 1)
            trial_genes = set([g.upper() for g in criteria.get("required_genes", [])])
            overlap = p_genes.intersection(trial_genes)
            if overlap:
                genomic_score = 1.0
            elif not trial_genes:
                genomic_score = 0.5  # Basket or biomarker-agnostic trial
            else:
                genomic_score = 0.0

            # 2. Condition / Indication Score (0 to 1)
            t_conditions = [c.lower() for c in trial.get("conditions", [])]
            cond_score = 0.0
            if any(p_diag in c or c in p_diag for c in t_conditions if p_diag):
                cond_score = 1.0
            elif any("solid tumor" in c for c in t_conditions):
                cond_score = 0.8  # Pan-solid tumor basket trial
            elif not p_diag:
                cond_score = 0.5

            # 3. Stage Score (0 to 1)
            t_stages = [s.lower() for s in criteria.get("stages", [])]
            stage_score = 1.0 if any(p_stage in s or s in p_stage for s in t_stages) else 0.4

            # 4. Criteria & Performance Score (0 to 1)
            perf_score = 1.0 if not eval_res["violations"] else 0.0

            # Composite match score
            if eval_res["violations"]:
                match_score = 0.0
                match_type = "disqualified"
            else:
                match_score = (
                    genomic_score * 0.40 +
                    cond_score * 0.30 +
                    stage_score * 0.15 +
                    perf_score * 0.15
                )

                if genomic_score >= 0.8 and cond_score >= 0.8:
                    match_type = "full"
                elif genomic_score >= 0.8 and cond_score < 0.8:
                    match_type = "biomarker_basket"
                elif cond_score >= 0.8:
                    match_type = "condition_only"
                else:
                    match_type = "partial"

            results.append({
                "trialId": trial.get("trialId"),
                "title": trial.get("title"),
                "phase": trial.get("phase", "Phase II"),
                "status": trial.get("status", "Active"),
                "conditions": trial.get("conditions", []),
                "drugs": trial.get("drugs", []),
                "biomarkers": trial.get("biomarkers", []),
                "sponsor": trial.get("sponsor", "Investigator Initiated"),
                "locations": trial.get("locations", []),
                "matchScore": round(float(match_score), 3),
                "matchType": match_type,
                "isEligible": eval_res["is_eligible"],
                "matchedCriteria": eval_res["matched_criteria"],
                "unmatchedCriteria": eval_res["unmatched_criteria"],
                "violations": eval_res["violations"]
            })

        return results
