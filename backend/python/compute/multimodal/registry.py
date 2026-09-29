import time
from backend.python.compute.multimodal.pathology.wsi_loader import WSILoader
from backend.python.compute.multimodal.pathology.tiler import SlideTiler
from backend.python.compute.multimodal.pathology.segmentor import TumorSegmentor
from backend.python.compute.multimodal.pathology.purity import TumorPurityEstimator
from backend.python.compute.multimodal.pathology.feature_extractor import MorphologyFeatureExtractor
from backend.python.compute.multimodal.radiology.loader import RadiologyLoader
from backend.python.compute.multimodal.radiology.ct_segmentor import CTSegmentor
from backend.python.compute.multimodal.radiology.mri_segmentor import MRISegmentor
from backend.python.compute.multimodal.radiology.radiomics import RadiomicsExtractor
from backend.python.compute.multimodal.retrieval.search import SlideSearchEngine
from backend.python.compute.multimodal.fusion.feature_fusion import FeatureFusionEngine
from backend.python.compute.multimodal.spatial.clustering import SpatialCellClusterer
from backend.python.compute.multimodal.spatial.neighborhood import CellNeighborhoodAnalyzer
from backend.python.compute.multimodal.explainability.gradcam import GradCAMGenerator
from backend.python.compute.multimodal.explainability.attention import AttentionRollout

class MultimodalRegistry:
    """
    Top-level registry and orchestrator for multimodal imaging intelligence pipelines.
    Composes pathology, radiology, retrieval, fusion, spatial, and explainability modules.
    """

    @staticmethod
    def run_pathology_pipeline(slide_path, patch_size=256):
        """
        Orchestrates: WSILoader -> SlideTiler -> TumorSegmentor ->
        TumorPurityEstimator -> MorphologyFeatureExtractor -> GradCAMGenerator.
        """
        start = time.perf_counter()

        # 1. Load slide metadata
        slide_metadata = WSILoader.load_slide(slide_path)

        # 2. Tile slide into patches
        patch_coords = SlideTiler.tile_slide(slide_metadata, patch_size=patch_size)

        # 3. Segment all patches
        patches = [{"pixels": [[0] * 64] * 64, "index": c.get("patch_index", i)} for i, c in enumerate(patch_coords)]
        segmentation = TumorSegmentor.segment_slide(patches)

        # 4. Estimate purity & necrosis
        purity = TumorPurityEstimator.estimate_purity(segmentation)

        # 5. Extract morphology features
        features = MorphologyFeatureExtractor.extract_features(segmentation)

        # 6. Generate GradCAM heatmap
        gradcam = GradCAMGenerator.generate_heatmap(patches[0] if patches else {"pixels": [[0]*32]*32})

        elapsed = (time.perf_counter() - start) * 1000.0

        return {
            "slide_metadata": slide_metadata,
            "segmentation": segmentation,
            "purity": purity,
            "features": features,
            "gradcam": gradcam,
            "processing_time_ms": round(elapsed, 2)
        }

    @staticmethod
    def run_radiology_pipeline(scan_path, modality='ct'):
        """
        Orchestrates: RadiologyLoader -> CT/MRI Segmentor -> RadiomicsExtractor.
        """
        start = time.perf_counter()

        # 1. Load scan
        if modality == 'mri':
            scan_metadata = RadiologyLoader.load_nifti(scan_path)
        else:
            scan_metadata = RadiologyLoader.load_dicom(scan_path)

        # 2. Segment volume
        volume_data = {"slices": scan_metadata.get("slice_count", 120)}
        if modality == 'mri':
            segmentation = MRISegmentor.segment_volume(volume_data)
        else:
            segmentation = CTSegmentor.segment_volume(volume_data)

        # 3. Extract radiomics features
        radiomics = RadiomicsExtractor.extract_all_features(segmentation)

        elapsed = (time.perf_counter() - start) * 1000.0

        return {
            "scan_metadata": scan_metadata,
            "segmentation": segmentation,
            "radiomics": radiomics,
            "processing_time_ms": round(elapsed, 2)
        }

    @staticmethod
    def run_slide_retrieval(query_embedding, top_k=5):
        """
        Runs ANN slide retrieval via SlideSearchEngine.
        Pre-populates index with mock cohort slides.
        """
        engine = SlideSearchEngine()

        # Pre-populate with mock indexed slides
        for i in range(10):
            vec = [0.5 + (i * 0.03)] * len(query_embedding)
            engine.index_slide(f"TCGA-OV-{1000 + i}", vec)

        result = engine.search(query_embedding, top_k=top_k)
        return result

    @staticmethod
    def run_feature_fusion(image_features, genomic_features):
        """
        Fuses image + genomic vectors and updates Digital Twin simulation params.
        """
        fusion_result = FeatureFusionEngine.fuse_image_genomic(image_features, genomic_features)

        purity_data = {}
        if isinstance(image_features, dict):
            purity_data = {
                "purity": image_features.get("tumor_purity_percent", 80.0),
                "mitosis_rate": image_features.get("mitosis_count_per_hpf", 0),
                "lymphocyte_density": image_features.get("lymphocyte_density", 0)
            }
        else:
            purity_data = {"purity": 80.0}

        twin_updates = FeatureFusionEngine.update_digital_twin_params(purity_data)

        return {
            "fusion": fusion_result,
            "twin_param_updates": twin_updates
        }

    @staticmethod
    def run_spatial_analysis(cell_positions, cell_types=None):
        """
        Runs SpatialCellClusterer + CellNeighborhoodAnalyzer -> combined spatial metrics.
        """
        clustering = SpatialCellClusterer.cluster_cells(cell_positions)

        neighborhood = {}
        if cell_types:
            neighborhood = CellNeighborhoodAnalyzer.neighborhood_composition(cell_positions, cell_types)

        hotspots = SpatialCellClusterer.identify_hotspots(cell_positions)

        return {
            "clustering": clustering,
            "neighborhood_composition": neighborhood,
            "hotspots": hotspots
        }
