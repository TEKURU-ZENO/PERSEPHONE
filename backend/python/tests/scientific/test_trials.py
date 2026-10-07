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
            "recruitment_status": "Active, Recruiting",
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

    def test_protein_change_normalization(self):
        self.assertEqual(EligibilityExtractor.normalize_protein_change("p.Gly12Asp"), "G12D")
        self.assertEqual(EligibilityExtractor.normalize_protein_change("Gly12Asp"), "G12D")
        self.assertEqual(EligibilityExtractor.normalize_protein_change("p.Leu858Arg"), "L858R")
        self.assertEqual(EligibilityExtractor.normalize_protein_change("Leu858Arg"), "L858R")
        self.assertEqual(EligibilityExtractor.normalize_protein_change("p.Arg273His"), "R273H")
        self.assertEqual(EligibilityExtractor.normalize_protein_change("G12C"), "G12C")
        self.assertEqual(EligibilityExtractor.normalize_protein_change("p.G12C"), "G12C")
        self.assertEqual(EligibilityExtractor.normalize_protein_change("MET Amp (CN=6)"), "Amplification")
        self.assertEqual(EligibilityExtractor.normalize_protein_change("Amplification"), "Amplification")

    def test_patient_specific_trial_matching_and_filtering(self):
        # Patient C: Colorectal, KRAS G12D, MSS
        patient_c = {
            "cancerType": "colorectal",
            "diagnosis": "Colorectal Adenocarcinoma",
            "stage": "Stage IV (Hepatic Metastases)",
            "microsatellite_status": "MSS",
            "variants": [
                {"gene": "KRAS", "alteration": "G12D", "tier": "Tier I-A"},
                {"gene": "APC", "alteration": "I1307K", "tier": "Tier II-C"},
                {"gene": "TP53", "alteration": "R175H", "tier": "Tier I-B"}
            ],
            "age": 49,
            "country": "United States",
            "city": "New York"
        }
        res_c = ClinicalTrialsRegistry.run_trial_matching_pipeline(patient_c)
        matched_c = res_c["matchedTrials"]
        screened_c = res_c["allScreenedTrials"]

        # Rule 1: No KRYSTAL-1 matched, and rejection reason is G12C mutation mismatch, not cancer type
        self.assertNotIn("NCT03785249", [t["trialId"] for t in matched_c])
        krystal1 = next((t for t in screened_c if t["trialId"] == "NCT03785249"), None)
        self.assertIsNotNone(krystal1)
        self.assertTrue(any("Mutation mismatch: Trial requires KRAS G12C" in v for v in krystal1["violations"]))
        self.assertFalse(any("Cancer type mismatch" in v for v in krystal1["violations"]))

        # Rule 2: No KEYNOTE-177 matched, rejected for MSS status
        self.assertNotIn("NCT02563002", [t["trialId"] for t in matched_c])
        kn177 = next((t for t in screened_c if t["trialId"] == "NCT02563002"), None)
        self.assertIsNotNone(kn177)
        self.assertTrue(any("Biomarker mismatch: Trial requires MSI-H/dMMR, patient has MSS" in v for v in kn177["violations"]))

        # Rule 3: No trials from other cancer types (ovarian, lung, prostate, breast)
        for t in matched_c:
            self.assertTrue(
                "colorectal" in t.get("cancer_types", []) or "solid_tumor" in t.get("cancer_types", [])
            )
        self.assertIsNone(res_c["topTrial"])

        # Patient B: Lung NSCLC, EGFR L858R + MET amp, progression on osimertinib, no platinum chemotherapy
        patient_b = {
            "cancerType": "nsclc",
            "diagnosis": "Lung Adenocarcinoma (NSCLC)",
            "stage": "Stage IV (Bone Metastases)",
            "prior_therapies": ["First-line osimertinib"],
            "variants": [
                {"gene": "EGFR", "alteration": "L858R", "tier": "Tier I-A"},
                {"gene": "MET", "alteration": "Amplification", "tier": "Tier I-B"},
                {"gene": "TP53", "alteration": "R273H", "tier": "Tier I-B"}
            ],
            "age": 68,
            "country": "United States",
            "city": "New York"
        }
        res_b = ClinicalTrialsRegistry.run_trial_matching_pipeline(patient_b)
        matched_b = res_b["matchedTrials"]
        matched_b_ids = [t["trialId"] for t in matched_b]

        # Must match ORCHARD, MARIPOSA-2, and CHRYSALIS-2 as non-enrolling supporting evidence
        self.assertIn("NCT03944772", matched_b_ids)  # ORCHARD
        self.assertIn("NCT04988295", matched_b_ids)  # MARIPOSA-2
        self.assertIn("NCT04077463", matched_b_ids)  # CHRYSALIS-2

        # All three post-osimertinib trials are active but closed to enrollment -> "biomarker match, not enrolling"
        for tid in ["NCT03944772", "NCT04988295", "NCT04077463"]:
            trial = next(t for t in matched_b if t["trialId"] == tid)
            self.assertEqual(trial["status_label"], "biomarker match, not enrolling")
            self.assertFalse(trial["isEligible"])

        # Zero trials for ovarian, colorectal, or prostate
        for t in matched_b:
            c_types = t.get("cancer_types", [])
            self.assertTrue("nsclc" in c_types or "solid_tumor" in c_types)
            self.assertNotIn("ovarian", c_types)
            self.assertNotIn("colorectal", c_types)
            self.assertNotIn("prostate", c_types)

    def test_fixture_built_panel_request_matching(self):
        """
        Tests the exact endpoint payload built by ClinicalTrialsPanel.js from patient fixtures.
        Verifies:
        - Patient A: PETRA & NCT04633239 blocked; NRG-GY036 matched & eligible; topTrial is NRG-GY036.
        - Patient B: FLAURA excluded; ORCHARD, MARIPOSA-2, CHRYSALIS-2 matched as non-enrolling; topTrial is None.
        - Patient C: KRYSTAL-1 & KEYNOTE-177 blocked; zero matches; topTrial is None.
        """
        from backend.python.compute.registry import ComputeRegistry

        # 1. Patient A: Elena Rostova (HGSOC, Stage IIIC, BRCA1 somatic, prior carbo/pacli)
        payload_a = {
            "patientId": "patient-a",
            "cancerType": "ovarian",
            "diagnosis": "High-Grade Serous Ovarian Cancer (HGSOC)",
            "stage": "Stage IIIC",
            "microsatelliteStatus": "MSS (Stable)",
            "priorTherapies": ["carboplatin", "paclitaxel"],
            "variants": [
                {"gene": "BRCA1", "alteration": EligibilityExtractor.normalize_protein_change("p.Glu654Glyfs*14")},
                {"gene": "TP53", "alteration": EligibilityExtractor.normalize_protein_change("p.Arg273His")},
                {"gene": "MYC", "alteration": "Amplification"}
            ],
            "age": 54,
            "country": "United States"
        }
        res_a = ComputeRegistry.run_trial_matching(payload_a)["result"]
        matched_a_ids = [t["trialId"] for t in res_a["matchedTrials"]]

        # PETRA (requires Advanced, Metastatic; patient is Stage IIIC) must NOT match
        self.assertNotIn("NCT04644068", matched_a_ids)
        # NCT04633239 (requires Recurrent, Platinum-Resistant; patient is newly diagnosed) must NOT match
        self.assertNotIn("NCT04633239", matched_a_ids)
        # Actively recruiting trial NRG-GY036 must match and be eligible
        self.assertIn("NCT06580314", matched_a_ids)
        nrg = next(t for t in res_a["matchedTrials"] if t["trialId"] == "NCT06580314")
        self.assertTrue(nrg["isEligible"])
        self.assertEqual(nrg["status_label"], "eligible")
        # topTrial must be the recruiting trial NRG-GY036
        self.assertIsNotNone(res_a["topTrial"])
        self.assertEqual(res_a["topTrial"]["trialId"], "NCT06580314")
        self.assertEqual(res_a["totalEligible"], 1)

        # 2. Patient B: Arthur Pendelton (NSCLC, Stage IV, EGFR L858R + MET amp, prior osimertinib)
        payload_b = {
            "patientId": "patient-b",
            "cancerType": "nsclc",
            "diagnosis": "Lung Adenocarcinoma (NSCLC)",
            "stage": "Stage IV (Bone Metastases)",
            "microsatelliteStatus": "MSS (Stable)",
            "priorTherapies": ["osimertinib"],
            "variants": [
                {"gene": "EGFR", "alteration": EligibilityExtractor.normalize_protein_change("p.Leu858Arg")},
                {"gene": "MET", "alteration": "Amplification"}
            ],
            "age": 68,
            "country": "United States"
        }
        res_b = ComputeRegistry.run_trial_matching(payload_b)["result"]
        matched_b_ids = [t["trialId"] for t in res_b["matchedTrials"]]

        # FLAURA (treatment-naive; excludes prior EGFR TKI) must NOT match
        self.assertNotIn("NCT02296125", matched_b_ids)
        # Closed trials match as supporting evidence
        self.assertIn("NCT03944772", matched_b_ids)  # ORCHARD
        self.assertIn("NCT04988295", matched_b_ids)  # MARIPOSA-2
        self.assertIn("NCT04077463", matched_b_ids)  # CHRYSALIS-2
        for t in res_b["matchedTrials"]:
            self.assertFalse(t["isEligible"])
            self.assertEqual(t["status_label"], "biomarker match, not enrolling")
        # Only recruiting trials can be topTrial -> topTrial must be None
        self.assertIsNone(res_b["topTrial"])
        self.assertEqual(res_b["totalEligible"], 0)

        # 3. Patient C: Marcus Vance (Colorectal, Stage IV, KRAS G12D, MSS, prior FOLFIRI/bevacizumab)
        payload_c = {
            "patientId": "patient-c",
            "cancerType": "colorectal",
            "diagnosis": "Colorectal Adenocarcinoma",
            "stage": "Stage IV (Hepatic Metastases)",
            "microsatelliteStatus": "MSS (Stable)",
            "priorTherapies": ["FOLFIRI", "bevacizumab"],
            "variants": [
                {"gene": "KRAS", "alteration": EligibilityExtractor.normalize_protein_change("p.Gly12Asp")}
            ],
            "age": 49,
            "country": "United States"
        }
        res_c = ComputeRegistry.run_trial_matching(payload_c)["result"]
        # Negative screen: zero matching trials in active registry
        self.assertEqual(len(res_c["matchedTrials"]), 0)
        self.assertIsNone(res_c["topTrial"])
        self.assertEqual(res_c["totalEligible"], 0)

if __name__ == '__main__':
    unittest.main()

