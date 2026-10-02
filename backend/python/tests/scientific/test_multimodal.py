import unittest
from backend.python.compute.multimodal.pathology.wsi_loader import WSILoader
from backend.python.compute.multimodal.pathology.tiler import SlideTiler
from backend.python.compute.multimodal.pathology.segmentor import TumorSegmentor
from backend.python.compute.multimodal.pathology.purity import TumorPurityEstimator
from backend.python.compute.multimodal.pathology.feature_extractor import MorphologyFeatureExtractor
from backend.python.compute.multimodal.radiology.loader import RadiologyLoader
from backend.python.compute.multimodal.radiology.ct_segmentor import CTSegmentor
from backend.python.compute.multimodal.radiology.mri_segmentor import MRISegmentor
from backend.python.compute.multimodal.radiology.radiomics import RadiomicsExtractor
from backend.python.compute.multimodal.retrieval.similarity import SimilarityScorer
from backend.python.compute.multimodal.retrieval.search import SlideSearchEngine
from backend.python.compute.multimodal.fusion.feature_fusion import FeatureFusionEngine
from backend.python.compute.multimodal.spatial.clustering import SpatialCellClusterer
from backend.python.compute.multimodal.spatial.neighborhood import CellNeighborhoodAnalyzer
from backend.python.compute.multimodal.explainability.gradcam import GradCAMGenerator
from backend.python.compute.multimodal.explainability.attention import AttentionRollout
from backend.python.compute.multimodal.registry import MultimodalRegistry

class TestWSILoader(unittest.TestCase):
  def test_load_slide_returns_metadata(self):
    result = WSILoader.load_slide("slides/test.svs")
    self.assertIn("dimensions", result)
    self.assertIn("magnification", result)
    self.assertIn("tile_count", result)

class TestSlideTiler(unittest.TestCase):
  def test_tile_slide_generates_patches(self):
    metadata = WSILoader.load_slide("slides/test.svs")
    patches = SlideTiler.tile_slide(metadata, patch_size=256)
    self.assertIsInstance(patches, list)
    self.assertGreater(len(patches), 0)
    self.assertIn("x", patches[0])
    self.assertIn("y", patches[0])

class TestTumorSegmentor(unittest.TestCase):
  def test_segment_patch(self):
    result = TumorSegmentor.segment_patch({"pixels": [[0]*64]*64})
    self.assertIn("tumor_area_fraction", result)
    self.assertIn("confidence", result)

  def test_segment_slide_aggregation(self):
    patches = [{"pixels": [[i]*64]*64} for i in range(10)]
    result = TumorSegmentor.segment_slide(patches)
    self.assertIn("total_patches", result)
    self.assertIn("tumor_patches", result)
    self.assertIn("overall_tumor_fraction", result)

  def test_model_info(self):
    info = TumorSegmentor.get_model_info()
    self.assertEqual(info["model_name"], "UNet-ResNet50")

class TestTumorPurity(unittest.TestCase):
  def test_estimate_purity(self):
    seg = {
      "total_patches": 100,
      "tumor_patches": 72,
      "overall_tumor_fraction": 0.72,
      "necrosis_percent": 5.0,
      "stroma_percent": 15.0
    }
    result = TumorPurityEstimator.estimate_purity(seg)
    self.assertIn("tumor_purity_percent", result)
    self.assertIn("necrosis_percent", result)
    self.assertIn("cellularity_index", result)
    self.assertEqual(result["tumor_purity_percent"], 72.0)
    self.assertEqual(result["necrosis_percent"], 5.0)
    self.assertEqual(result["stroma_percent"], 15.0)
    self.assertEqual(result["viable_tumor_percent"], 67.0)

  def test_independent_morphology_invariance(self):
    # Tumor, necrosis, and stroma are independent; not fixed fractional multipliers
    seg_high_tumor_zero_necrosis = {
      "tumor_purity_percent": 80.0,
      "necrosis_percent": 0.0,
      "stroma_percent": 20.0
    }
    res1 = TumorPurityEstimator.estimate_purity(seg_high_tumor_zero_necrosis)
    self.assertEqual(res1["tumor_purity_percent"], 80.0)
    self.assertEqual(res1["necrosis_percent"], 0.0)
    self.assertEqual(res1["viable_tumor_percent"], 80.0)

    seg_low_tumor_high_necrosis = {
      "tumor_purity_percent": 20.0,
      "necrosis_percent": 60.0,
      "stroma_percent": 10.0
    }
    res2 = TumorPurityEstimator.estimate_purity(seg_low_tumor_high_necrosis)
    self.assertEqual(res2["tumor_purity_percent"], 20.0)
    self.assertEqual(res2["necrosis_percent"], 60.0)
    self.assertEqual(res2["viable_tumor_percent"], 0.0) # max(0, 20 - 60)

class TestMorphologyFeatures(unittest.TestCase):
  def test_extract_features(self):
    seg = {"total_patches": 100, "tumor_patches": 72, "overall_tumor_fraction": 0.72}
    result = MorphologyFeatureExtractor.extract_features(seg)
    self.assertIn("lymphocyte_density", result)
    self.assertIn("nuclear_density", result)
    self.assertIn("mitosis_count_per_hpf", result)
    self.assertIn("tumor_infiltrating_lymphocytes_score", result)

  def test_feature_names(self):
    names = MorphologyFeatureExtractor.get_feature_names()
    self.assertIsInstance(names, list)
    self.assertGreater(len(names), 5)

class TestRadiologyLoader(unittest.TestCase):
  def test_load_dicom(self):
    result = RadiologyLoader.load_dicom("scans/test.dcm")
    self.assertIn("modality", result)
    self.assertIn("dimensions", result)

  def test_load_nifti(self):
    result = RadiologyLoader.load_nifti("scans/test.nii")
    self.assertIn("dimensions", result)
    self.assertIn("voxel_spacing", result)

class TestCTSegmentor(unittest.TestCase):
  def test_segment_volume(self):
    result = CTSegmentor.segment_volume({"slices": 120})
    self.assertIn("tumor_volume_cm3", result)
    self.assertIn("max_diameter_mm", result)
    self.assertGreater(result["tumor_volume_cm3"], 0)

class TestMRISegmentor(unittest.TestCase):
  def test_segment_volume(self):
    result = MRISegmentor.segment_volume({"slices": 80})
    self.assertIn("tumor_volume_cm3", result)
    self.assertIn("enhancement_ratio", result)

class TestRadiomics(unittest.TestCase):
  def test_extract_all_features(self):
    seg = {"tumor_volume_cm3": 12.5, "max_diameter_mm": 35.0}
    result = RadiomicsExtractor.extract_all_features(seg)
    self.assertIn("shape_features", result)
    self.assertIn("texture_features", result)
    self.assertIn("volume", result["shape_features"])
    self.assertIn("glcm_contrast", result["texture_features"])

class TestSimilarityScorer(unittest.TestCase):
  def test_cosine_similarity(self):
    vec_a = [1.0, 0.0, 0.0]
    vec_b = [1.0, 0.0, 0.0]
    sim = SimilarityScorer.cosine_similarity(vec_a, vec_b)
    self.assertAlmostEqual(sim, 1.0, places=5)

  def test_euclidean_distance(self):
    vec_a = [0.0, 0.0]
    vec_b = [3.0, 4.0]
    dist = SimilarityScorer.euclidean_distance(vec_a, vec_b)
    self.assertAlmostEqual(dist, 5.0, places=5)

class TestSlideSearchEngine(unittest.TestCase):
  def test_index_and_search(self):
    engine = SlideSearchEngine()
    engine.index_slide("slide-001", [0.5] * 64)
    engine.index_slide("slide-002", [0.8] * 64)
    engine.index_slide("slide-003", [0.2] * 64)
    result = engine.search([0.5] * 64, top_k=2)
    self.assertIn("matches", result)
    self.assertEqual(len(result["matches"]), 2)

class TestFeatureFusion(unittest.TestCase):
  def test_fuse_image_genomic(self):
    image_feats = {"lymphocyte_density": 45, "nuclear_density": 120}
    genomic_feats = {"brca1_status": 1, "expression_profile": [0.8, 0.3]}
    result = FeatureFusionEngine.fuse_image_genomic(image_feats, genomic_feats)
    self.assertIn("fused_vector", result)
    self.assertIn("fusion_method", result)

  def test_update_digital_twin_params(self):
    purity = {"tumor_purity_percent": 80, "necrosis_percent": 10, "cellularity_index": 0.75}
    result = FeatureFusionEngine.update_digital_twin_params(purity)
    self.assertIn("carrying_capacity_K", result)
    self.assertGreater(result["carrying_capacity_K"], 0)

class TestSpatialClustering(unittest.TestCase):
  def test_cluster_cells(self):
    cells = [{"x": i * 10.0, "y": j * 10.0} for i in range(5) for j in range(5)]
    result = SpatialCellClusterer.cluster_cells(cells)
    self.assertIn("num_clusters", result)
    self.assertIn("silhouette_score", result)

class TestNeighborhoodAnalysis(unittest.TestCase):
  def test_immune_infiltration_score(self):
    tumor = [{"x": 0, "y": 0}, {"x": 10, "y": 10}]
    immune = [{"x": 5, "y": 5}, {"x": 50, "y": 50}]
    result = CellNeighborhoodAnalyzer.immune_infiltration_score(tumor, immune, radius=20.0)
    self.assertIn("infiltration_score", result)
    self.assertGreaterEqual(result["infiltration_score"], 0)
    self.assertLessEqual(result["infiltration_score"], 1)

class TestGradCAM(unittest.TestCase):
  def test_generate_heatmap(self):
    result = GradCAMGenerator.generate_heatmap({"pixels": [[0]*32]*32})
    self.assertIn("heatmap", result)
    self.assertIn("activation_stats", result)
    self.assertIsInstance(result["heatmap"], list)

class TestAttentionRollout(unittest.TestCase):
  def test_compute_attention_map(self):
    embeddings = [[0.5] * 64 for _ in range(8)]
    result = AttentionRollout.compute_attention_map(embeddings)
    self.assertIn("attention_weights", result)
    self.assertIn("entropy", result)

class TestMultimodalRegistry(unittest.TestCase):
  def test_run_pathology_pipeline(self):
    result = MultimodalRegistry.run_pathology_pipeline("slides/test.svs")
    self.assertIn("slide_metadata", result)
    self.assertIn("segmentation", result)
    self.assertIn("purity", result)
    self.assertIn("features", result)
    self.assertIn("processing_time_ms", result)

  def test_run_radiology_pipeline(self):
    result = MultimodalRegistry.run_radiology_pipeline("scans/test.dcm", modality="ct")
    self.assertIn("scan_metadata", result)
    self.assertIn("segmentation", result)
    self.assertIn("radiomics", result)

  def test_run_slide_retrieval(self):
    result = MultimodalRegistry.run_slide_retrieval([0.5] * 128, top_k=3)
    self.assertIn("matches", result)

if __name__ == '__main__':
  unittest.main()
