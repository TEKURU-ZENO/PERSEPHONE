import unittest
from backend.python.compute.trials.trial_registry import TrialRegistry
from backend.python.compute.trials.eligibility_extractor import EligibilityExtractor
from backend.python.compute.trials.trial_matcher import TrialMatcher
from backend.python.compute.trials.trial_ranker import TrialRanker
from backend.python.compute.trials.geographic_filter import GeographicFilter
from backend.python.compute.trials.registry import ClinicalTrialsRegistry

class TestTrialRegistry(unittest.TestCase):
    def test_load_trials(self):
        trials = TrialRegistry.load_trials(force_reload=True)
        self.assertIsInstance(trials, list)
        self.assertGreaterEqual(len(trials), 10)
        self.assertIn("trialId", trials[0])
        self.assertIn("conditions", trials[0])

    def test_get_trial_by_id(self):
        trial = TrialRegistry.get_trial("NCT03737643")
        self.assertIsNotNone(trial)
        self.assertEqual(trial.get("trialId"), "NCT03737643")

    def test_filter_by_phase(self):
        phase3 = TrialRegistry.filter_by_phase(["Phase III"])
        self.assertGreater(len(phase3), 0)
        for t in phase3:
            self.assertIn("Phase III", t.get("phase"))

    def test_filter_by_biomarker(self):
        brca_trials = TrialRegistry.filter_by_biomarker("BRCA1")
        self.assertGreater(len(brca_trials), 0)

    def test_online_or_fallback_fetch(self):
        # Must execute cleanly with either live online data or local database fallback
        res = TrialRegistry.fetch_online_trials("BRCA1", max_results=2)
        self.assertIn("trials", res)
        self.assertIn("online", res)
        self.assertGreater(len(res["trials"]), 0)

class TestEligibilityExtractor(unittest.TestCase):
    def test_extract_criteria(self):
        text = "Inclusion: Pathogenic BRCA1 or BRCA2 mutation. Stage III or Stage IV. ECOG <= 1. Age >= 18. Exclusion: untreated brain metastases."
        criteria = EligibilityExtractor.extract_criteria(text)
        self.assertIn("BRCA1", criteria["required_genes"])
        self.assertIn("BRCA2", criteria["required_genes"])
        self.assertIn("Stage III", criteria["stages"])
        self.assertEqual(criteria["max_ecog"], 1)
        self.assertEqual(criteria["min_age"], 18)
        self.assertGreater(len(criteria["exclusions"]), 0)

    def test_evaluate_eligibility(self):
        criteria = {
            "required_genes": ["BRCA1"],
            "stages": ["Stage III", "Stage IV"],
            "max_ecog": 2,
            "min_age": 18,
            "exclusions": [{"key": "brain metastases", "description": "active CNS metastases"}]
        }
        # Eligible patient
        patient_good = {
            "variants": ["BRCA1"],
            "stage": "Stage III",
            "ecog": 1,
            "age": 55,
            "has_active_cns_metastases": False
        }
        res_good = EligibilityExtractor.evaluate_eligibility(patient_good, criteria)
        self.assertTrue(res_good["is_eligible"])
        self.assertEqual(len(res_good["violations"]), 0)

        # Ineligible patient (exclusion conflict)
        patient_bad = {
            "variants": ["BRCA1"],
            "stage": "Stage III",
            "ecog": 1,
            "age": 55,
            "has_active_cns_metastases": True
        }
        res_bad = EligibilityExtractor.evaluate_eligibility(patient_bad, criteria)
        self.assertFalse(res_bad["is_eligible"])
        self.assertGreater(len(res_bad["violations"]), 0)

class TestTrialMatcher(unittest.TestCase):
    def test_match_patient(self):
        patient = {
            "variants": ["BRCA1"],
            "diagnosis": "Ovarian Cancer",
            "stage": "Stage III",
            "ecog": 1,
            "age": 58
        }
        trials = TrialRegistry.load_trials()
        matches = TrialMatcher.match_patient_to_trials(patient, trials)
        self.assertEqual(len(matches), len(trials))
        
        # Check first match structure
        first = matches[0]
        self.assertIn("matchScore", first)
        self.assertIn("matchType", first)
        self.assertIn("isEligible", first)
        self.assertGreater(first["matchScore"], 0.0)

class TestTrialRanker(unittest.TestCase):
    def test_rank_trials(self):
        sample_matches = [
            {"trialId": "T1", "matchScore": 0.95, "phase": "Phase III", "status": "Active, Recruiting", "biomarkers": ["BRCA1"], "isEligible": True, "matchType": "full"},
            {"trialId": "T2", "matchScore": 0.70, "phase": "Phase I", "status": "Active", "biomarkers": ["UNKNOWN"], "isEligible": True, "matchType": "partial"},
            {"trialId": "T3", "matchScore": 0.0, "phase": "Phase II", "status": "Active", "biomarkers": [], "isEligible": False, "matchType": "disqualified"}
        ]
        ranked = TrialRanker.rank_trials(sample_matches)
        self.assertEqual(len(ranked), 3)
        self.assertEqual(ranked[0]["trialId"], "T1")
        self.assertEqual(ranked[0]["rank"], 1)
        self.assertGreater(ranked[0]["compositeScore"], ranked[1]["compositeScore"])
        self.assertEqual(ranked[2]["trialId"], "T3")

class TestGeographicFilter(unittest.TestCase):
    def test_annotate_geography(self):
        sample = [{
            "trialId": "NCT03737643",
            "locations": [
                {"country": "United States", "city": "New York", "facility": "MSKCC"},
                {"country": "United States", "city": "Boston", "facility": "DFCI"}
            ]
        }]
        annotated = GeographicFilter.annotate_geography(sample, patient_country="United States", patient_city="New York")
        self.assertEqual(len(annotated), 1)
        self.assertEqual(annotated[0]["distanceCategory"], "local")
        self.assertTrue(annotated[0]["isLocal"])

class TestClinicalTrialsRegistry(unittest.TestCase):
    def test_run_trial_matching_pipeline(self):
        profile = {
            "variants": ["BRCA1"],
            "diagnosis": "Ovarian Cancer",
            "stage": "Stage III",
            "biomarker_tier": "Tier I-A",
            "age": 58,
            "country": "United States",
            "city": "New York"
        }
        res = ClinicalTrialsRegistry.run_trial_matching_pipeline(profile)
        self.assertIn("matchedTrials", res)
        self.assertIn("topTrial", res)
        self.assertIn("totalScreened", res)
        self.assertIn("totalEligible", res)
        self.assertIn("matchRate", res)
        self.assertGreater(res["totalScreened"], 0)
        self.assertIsNotNone(res["topTrial"])
        self.assertEqual(res["topTrial"]["rank"], 1)

if __name__ == '__main__':
    unittest.main()
