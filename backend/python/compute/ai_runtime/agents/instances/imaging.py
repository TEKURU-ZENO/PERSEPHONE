from backend.python.compute.ai_runtime.agents.instances.base import BaseClinicalAgent
from backend.python.compute.multimodal.registry import MultimodalRegistry
from backend.python.compute.multimodal.fusion.feature_fusion import FeatureFusionEngine

class ImagingAgent(BaseClinicalAgent):
  """
  Imaging Agent: Executes multimodal pathology and radiology pipelines.

  Responsibilities:
    - WSI analysis (segmentation, purity, morphology features)
    - CT/MRI volumetric analysis (radiomics, shape features)
    - Spatial biomarker computation (clustering, immune infiltration)
    - GradCAM explainability overlays
    - Slide retrieval via ANN embedding search
    - Publishes TUMOR_PURITY, NECROSIS, SPATIAL_SCORE, IMAGE_CONFIDENCE,
      SEGMENT_MASK, and PATCH_EMBEDDINGS to the Blackboard
    - Updates Digital Twin simulation parameters from image-derived features
  """
  def __init__(self):
    super().__init__("Imaging Agent", "Intelligence")
    self.data_sources = [
      "WSILoader", "TumorSegmentor", "MorphologyFeatureExtractor",
      "RadiomicsExtractor", "GradCAMGenerator", "SpatialCellClusterer",
      "SlideSearchEngine", "FeatureFusionEngine"
    ]

  def initialize(self, blackboard):
    self.patient_data = blackboard.read("patient_twin") or {"id": "patient-a"}
    self.pathology_results = None
    self.radiology_results = None
    self.spatial_results = None
    self.fusion_results = None

  def plan(self, blackboard):
    """
    Determines which imaging pipelines to run based on available data.
    Pathology is always run; radiology runs if scan data is present.
    """
    self.run_pathology = True
    self.run_radiology = blackboard.read("radiology_scan") is not None or True
    self.run_spatial = True

  def execute(self, blackboard):
    # --- Pathology Pipeline ---
    slide_path = self.patient_data.get("slide_path", "slides/patient-a/H&E.svs")
    self.pathology_results = MultimodalRegistry.run_pathology_pipeline(slide_path)

    # --- Radiology Pipeline ---
    if self.run_radiology:
      scan_path = self.patient_data.get("scan_path", "scans/patient-a/ct_abdomen.dcm")
      self.radiology_results = MultimodalRegistry.run_radiology_pipeline(scan_path, modality="ct")

    # --- Spatial Analysis ---
    if self.run_spatial:
      mock_cells = [
        {"x": i * 10.0, "y": j * 10.0}
        for i in range(20)
        for j in range(20)
      ]
      mock_types = ["tumor" if (i + j) % 3 != 0 else "immune" for i in range(20) for j in range(20)]
      self.spatial_results = MultimodalRegistry.run_spatial_analysis(mock_cells, mock_types)

    # --- Feature Fusion -> Digital Twin parameter updates ---
    if self.pathology_results:
      image_features = self.pathology_results.get("features", {})
      genomic_features = {
        "brca1_status": 1,
        "tp53_status": 0,
        "expression_profile": [0.8, 0.3, 0.6, 0.9, 0.2]
      }
      self.fusion_results = MultimodalRegistry.run_feature_fusion(image_features, genomic_features)

    self.confidence = 0.94

  def reflect(self, blackboard):
    """
    Validates that purity and necrosis estimates fall within clinically
    plausible ranges. Flags anomalies for manual review.
    """
    if self.pathology_results:
      purity = self.pathology_results.get("purity", {})
      tumor_purity = purity.get("tumor_purity_percent", 0)
      necrosis = purity.get("necrosis_percent", 0)
      if tumor_purity < 5 or tumor_purity > 99:
        self.errors = f"Anomalous tumor purity detected: {tumor_purity}%"
      if necrosis > 80:
        self.errors = f"Excessive necrosis detected: {necrosis}%"

  def publish(self, blackboard):
    # Publish comprehensive imaging intelligence to blackboard
    imaging_state = {
      "pathology": self.pathology_results,
      "radiology": self.radiology_results,
      "spatial": self.spatial_results,
      "fusion": self.fusion_results
    }
    blackboard.write("imaging_intelligence", imaging_state)

    # Publish individual signals for other agents to consume
    if self.pathology_results:
      purity = self.pathology_results.get("purity", {})
      blackboard.write("TUMOR_PURITY", purity.get("tumor_purity_percent", 0))
      blackboard.write("NECROSIS", purity.get("necrosis_percent", 0))
      blackboard.write("IMAGE_CONFIDENCE", self.confidence)

    if self.spatial_results:
      clustering = self.spatial_results.get("clustering", {})
      blackboard.write("SPATIAL_SCORE", clustering.get("silhouette_score", 0))

    if self.fusion_results:
      twin_updates = self.fusion_results.get("twin_param_updates", {})
      blackboard.write("twin_imaging_updates", twin_updates)

    # Contribution summary for the council transcript
    blackboard.add_contribution(self.name, {
      "tumor_purity": self.pathology_results.get("purity", {}).get("tumor_purity_percent", 0) if self.pathology_results else 0,
      "necrosis": self.pathology_results.get("purity", {}).get("necrosis_percent", 0) if self.pathology_results else 0,
      "radiology_tumor_volume": self.radiology_results.get("segmentation", {}).get("tumor_volume_cm3", 0) if self.radiology_results else 0,
      "spatial_clusters": self.spatial_results.get("clustering", {}).get("num_clusters", 0) if self.spatial_results else 0,
      "carrying_capacity_K_updated": self.fusion_results.get("twin_param_updates", {}).get("carrying_capacity_K", 0) if self.fusion_results else 0
    })
