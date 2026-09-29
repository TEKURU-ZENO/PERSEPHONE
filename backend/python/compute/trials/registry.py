"""
Clinical Trials Registry and Orchestration Pipeline for PERSEPHONE.
Coordinates trial ingestion, patient matching, ranking, geographic filtering,
and evidence integration.
"""
import time
from backend.python.compute.trials.trial_registry import TrialRegistry
from backend.python.compute.trials.trial_matcher import TrialMatcher
from backend.python.compute.trials.trial_ranker import TrialRanker
from backend.python.compute.trials.geographic_filter import GeographicFilter

class ClinicalTrialsRegistry:
    """
    Main entry point for Clinical Trials Intelligence compute pipelines.
    """

    @classmethod
    def run_trial_matching_pipeline(cls, patient_profile):
        """
        Runs the end-to-end clinical trial matching and ranking pipeline.
        
        Args:
            patient_profile (dict): Patient demographics, diagnosis, stage, variants, biomarkers.
            
        Returns:
            dict: Comprehensive matching and ranking report.
        """
        start_time = time.perf_counter()

        # 1. Ingest clinical trials
        all_trials = TrialRegistry.get_all_trials()

        # Check if online enrichment is explicitly requested
        if patient_profile.get("query_online"):
            primary_var = (patient_profile.get("variants") or ["BRCA1"])[0]
            online_res = TrialRegistry.fetch_online_trials(primary_var, max_results=3)
            if online_res.get("online"):
                # Append any new unique trials
                existing_ids = set([t.get("trialId") for t in all_trials])
                for ot in online_res.get("trials", []):
                    if ot.get("trialId") not in existing_ids:
                        all_trials.append(ot)

        # 2. Match patient against trial protocols
        matched_trials = TrialMatcher.match_patient_to_trials(patient_profile, all_trials)

        # 3. Composite clinical priority ranking
        genomic_context = {
            "actionability_tier": patient_profile.get("biomarker_tier", "Tier I-A")
        }
        ranked_trials = TrialRanker.rank_trials(matched_trials, genomic_context=genomic_context)

        # 4. Geographic distance and feasibility tagging
        patient_country = patient_profile.get("country", "United States")
        patient_city = patient_profile.get("city", "New York")
        geo_annotated = GeographicFilter.annotate_geography(
            ranked_trials,
            patient_country=patient_country,
            patient_city=patient_city
        )

        # Optional distance filter if provided
        allowed_distances = patient_profile.get("allowed_distance_categories")
        if allowed_distances:
            final_trials = GeographicFilter.filter_by_max_distance(geo_annotated, allowed_distances)
        else:
            final_trials = geo_annotated

        # 5. Summary metrics
        total_screened = len(all_trials)
        eligible_trials = [t for t in final_trials if t.get("isEligible", False)]
        total_eligible = len(eligible_trials)
        match_rate = round(total_eligible / max(total_screened, 1), 3)

        top_trial = final_trials[0] if final_trials else None
        processing_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return {
            "matchedTrials": final_trials,
            "topTrial": top_trial,
            "totalScreened": total_screened,
            "totalEligible": total_eligible,
            "matchRate": match_rate,
            "patientProfile": {
                "variants": patient_profile.get("variants", []),
                "diagnosis": patient_profile.get("diagnosis", ""),
                "stage": patient_profile.get("stage", "")
            },
            "processingTimeMs": processing_time_ms
        }
