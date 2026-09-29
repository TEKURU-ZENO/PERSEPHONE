import unittest
from backend.python.compute.response_intelligence.fusion import MultimodalResponseFusion, MultimodalResponseVector
from backend.python.compute.response_intelligence.biomarkers.digital import DigitalBiomarkerEngine
from backend.python.compute.response_intelligence.biomarkers.imaging import ImagingBiomarkerExtractor
from backend.python.compute.response_intelligence.biomarkers.genomic import GenomicBiomarkerExtractor
from backend.python.compute.response_intelligence.biomarkers.composite import CompositeBiomarkerSynthesizer
from backend.python.compute.response_intelligence.response.classifier import MultimodalResponseClassifier
from backend.python.compute.response_intelligence.response.predictor import TreatmentResponsePredictor
from backend.python.compute.response_intelligence.response.kinetics import ResponseKineticsModeler
from backend.python.compute.response_intelligence.resistance.detector import ResistanceMechanismDetector
from backend.python.compute.response_intelligence.resistance.predictor import ResistanceEscapePredictor
from backend.python.compute.response_intelligence.registry import ResponseIntelligenceRegistry

class TestMultimodalResponseFusion(unittest.TestCase):
    def test_fusion_with_complete_data(self):
        payload = {
            "patientId": "patient-a",
            "genomics": {"primary_variant": "BRCA1", "hrd_score": 45.0, "tmb": 8.5},
            "imaging": {"til_density": 0.70, "tumor_volume_cm3": 80.0},
            "pharmacogenomics": {"candidate_drug": "Olaparib", "synergy_score": 0.80, "predicted_ic50_um": 1.5},
            "monitoring": {"volume_velocity": -0.05, "ctdna_vaf_pct": 0.8}
        }
        vec = MultimodalResponseFusion.fuse(payload)
        self.assertIsInstance(vec, MultimodalResponseVector)
        self.assertEqual(vec.get_feature("genomic", "primary_variant"), "BRCA1")
        self.assertEqual(vec.get_feature("imaging", "til_density"), 0.70)
        self.assertEqual(vec.provenance["total_features"], len(vec.features))
        self.assertLessEqual(vec.provenance["missingness_ratio"], 0.20)

    def test_fusion_with_empty_payload_robustness(self):
        # Missing modalities must never crash the fusion engine
        vec = MultimodalResponseFusion.fuse({})
        self.assertIsInstance(vec, MultimodalResponseVector)
        self.assertGreaterEqual(vec.provenance["missingness_ratio"], 0.5)
        # Fallbacks work as expected and are marked as missing
        val = vec.get_feature("genomic", "hrd_score")
        self.assertIn(val, [58.0, 22.0])
        self.assertTrue(vec.genomic["hrd_score"].missingness)

class TestDigitalBiomarkers(unittest.TestCase):
    def setUp(self):
        self.vec = MultimodalResponseFusion.fuse({
            "genomics": {"primary_variant": "BRCA1", "hrd_score": 44.0, "tmb": 6.2},
            "imaging": {"tumor_purity": 80.0, "necrosis_ratio": 4.0, "til_density": 0.65},
            "pharmacogenomics": {"synergy_score": 0.78, "predicted_ic50_um": 1.6}
        })

    def test_digital_biomarker_engine(self):
        res = DigitalBiomarkerEngine.compute_digital_biomarker(self.vec)
        self.assertIn("value", res)
        self.assertTrue(0.0 <= res["value"] <= 1.0)
        self.assertEqual(res["calibration_status"], "research")
        self.assertEqual(res["model_version"], "digital-bm-v1")
        self.assertIn("uncertainty", res)

    def test_imaging_biomarker_extractor(self):
        res = ImagingBiomarkerExtractor.extract_imaging_biomarkers(self.vec)
        self.assertIn("value", res)
        self.assertTrue(0.0 <= res["value"] <= 1.0)
        self.assertIn("metrics", res)
        self.assertIn("viable_cellularity_ratio", res["metrics"])
        self.assertEqual(res["calibration_status"], "research")

    def test_genomic_biomarker_extractor(self):
        res = GenomicBiomarkerExtractor.extract_genomic_biomarkers(self.vec)
        self.assertIn("metrics", res)
        self.assertTrue(res["metrics"]["is_hrd_positive"])
        self.assertEqual(res["metrics"]["msi_status"], "MSS")
        self.assertEqual(res["calibration_status"], "research")

    def test_composite_biomarker_synthesizer(self):
        res = CompositeBiomarkerSynthesizer.synthesize_composite(self.vec)
        self.assertIn("value", res)
        self.assertTrue(0.0 <= res["value"] <= 1.0)
        self.assertIn(res["response_likelihood_tier"], ["Highly Favorable", "Favorable", "Intermediate", "Unfavorable"])
        self.assertIn("sub_scores", res)
        self.assertEqual(res["calibration_status"], "research")

class TestTreatmentResponsePredictor(unittest.TestCase):
    def setUp(self):
        self.vec = MultimodalResponseFusion.fuse({
            "genomics": {"primary_variant": "BRCA1", "hrd_score": 44.0},
            "imaging": {"til_density": 0.70},
            "pharmacogenomics": {"candidate_drug": "Olaparib", "synergy_score": 0.80, "predicted_ic50_um": 1.5},
            "monitoring": {"volume_velocity": -0.05, "ctdna_vaf_pct": 0.8}
        })

    def test_prediction_output_and_governance_metadata(self):
        pred = TreatmentResponsePredictor.predict_response(self.vec, proposed_drug="Olaparib")
        
        # Verify predicted_orr
        orr = pred["predicted_orr"]
        self.assertTrue(0.0 <= orr["value"] <= 1.0)
        self.assertEqual(orr["model_version"], "response-v1")
        self.assertEqual(orr["calibration_status"], "research")
        self.assertIn("uncertainty", orr)
        self.assertTrue(orr["uncertainty"]["lower_bound"] <= orr["value"] <= orr["uncertainty"]["upper_bound"])
        self.assertIn("evidence_basis", orr)

        # Verify predicted_pfs_days
        pfs = pred["predicted_pfs_days"]
        self.assertGreater(pfs["value"], 0.0) # Strictly non-negative
        self.assertEqual(pfs["model_version"], "response-v1")
        self.assertEqual(pfs["calibration_status"], "research")
        self.assertIn("uncertainty", pfs)
        self.assertGreaterEqual(pfs["uncertainty"]["lower_bound"], 0.0)

        # Verify predicted_depth_of_response
        depth = pred["predicted_depth_of_response"]
        self.assertLessEqual(depth["value"], 0.0) # Depth of response is negative shrinkage

class TestResponseClassifierAndKinetics(unittest.TestCase):
    def setUp(self):
        self.vec = MultimodalResponseFusion.fuse({
            "imaging": {"til_density": 0.65},
            "monitoring": {"volume_velocity": -0.06, "ctdna_vaf_pct": 0.5, "current_volume_cm3": 82.0},
            "pharmacogenomics": {"predicted_ic50_um": 1.8}
        })

    def test_multimodal_response_classifier(self):
        cls_res = MultimodalResponseClassifier.classify_response(self.vec)
        self.assertIn("category", cls_res)
        self.assertEqual(cls_res["category"], "Concordant Response")
        self.assertTrue(0.0 <= cls_res["concordance_score"] <= 1.0)
        self.assertEqual(cls_res["calibration_status"], "research")

    def test_response_kinetics_modeler(self):
        kin = ResponseKineticsModeler.model_kinetics(self.vec)
        self.assertGreater(kin["clearance_rate_constant"], 0.0)
        self.assertGreater(kin["projected_nadir_volume_cm3"], 0.0)
        self.assertTrue(60 <= kin["projected_time_to_nadir_days"] <= 240)
        self.assertEqual(len(kin["projected_trajectory"]), 7)
        self.assertEqual(kin["calibration_status"], "research")

class TestResistanceAndEscape(unittest.TestCase):
    def test_detect_resistance_mechanisms(self):
        # Scenario: BRCA1 patient with elevated ctDNA VAF indicates emerging secondary reversion
        vec = MultimodalResponseFusion.fuse({
            "genomics": {"primary_variant": "BRCA1"},
            "monitoring": {"ctdna_vaf_pct": 3.5, "volume_velocity": 0.06},
            "imaging": {"necrosis_ratio": 7.0}
        })
        res = ResistanceMechanismDetector.detect_mechanisms(vec)
        self.assertIn("state", res)
        self.assertIn(res["state"], ["Emerging Subclonal Resistance", "Acquired Resistance"])
        self.assertGreaterEqual(len(res["mechanisms"]), 1)
        genes = [m["gene"] for m in res["mechanisms"]]
        self.assertIn("BRCA1", genes)

    def test_predict_resistance_escape(self):
        vec = MultimodalResponseFusion.fuse({
            "genomics": {"primary_variant": "BRCA1"},
            "monitoring": {"ctdna_vaf_pct": 3.5, "volume_velocity": 0.06}
        })
        esc = ResistanceEscapePredictor.predict_escape(vec)
        risk = esc["resistance_risk"]["value"]
        ttar = esc["time_to_acquired_resistance_days"]["value"]
        self.assertTrue(0.0 <= risk <= 1.0)
        self.assertGreater(ttar, 0.0)
        self.assertEqual(esc["resistance_risk"]["calibration_status"], "research")
        self.assertGreaterEqual(len(esc["predicted_escape_pathways"]), 1)
        self.assertIn("candidate_drugs", esc["predicted_escape_pathways"][0])

class TestResponseIntelligenceRegistry(unittest.TestCase):
    def test_registry_extract_biomarkers(self):
        out = ResponseIntelligenceRegistry.extract_biomarkers({"genomics": {"primary_variant": "BRCA1"}})
        self.assertIn("digital", out)
        self.assertIn("imaging", out)
        self.assertIn("genomic", out)
        self.assertIn("composite", out)
        self.assertIn("processingTimeMs", out)

    def test_registry_predict_response(self):
        out = ResponseIntelligenceRegistry.predict_response({"genomics": {"primary_variant": "BRCA1"}}, proposed_drug="Olaparib")
        self.assertIn("prediction", out)
        self.assertIn("classification", out)
        self.assertIn("kinetics", out)
        self.assertIn("processingTimeMs", out)

    def test_registry_analyze_resistance(self):
        out = ResponseIntelligenceRegistry.analyze_resistance({"genomics": {"primary_variant": "BRCA1"}})
        self.assertIn("detection", out)
        self.assertIn("escape_prediction", out)
        self.assertIn("processingTimeMs", out)

    def test_registry_full_pipeline(self):
        out = ResponseIntelligenceRegistry.run_full_response_intelligence({"patientId": "patient-a"})
        self.assertIn("multimodal_vector", out)
        self.assertIn("biomarkers", out)
        self.assertIn("response", out)
        self.assertIn("resistance", out)

if __name__ == '__main__':
    unittest.main()
