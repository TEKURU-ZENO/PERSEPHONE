import hashlib
import json

class TumorSegmentor:
    """
    Clinical/Scientific Purpose:
    Segments key tissue compartments (tumor, stroma, necrosis, background) within H&E stained 
    slides. This serves as the foundation for automated computational biomarker extraction 
    (e.g., Tumor-Stroma Ratio).

    IMPORTANT IMPLEMENTATION NOTE:
    This module supports real segmentation mask inputs when provided. When operating in 
    standalone test/synthetic mode without loaded model weights or OpenSlide hardware acceleration,
    it explicitly tags results with `is_mock: True` and does NOT output fabricated confidence scores.
    """

    @staticmethod
    def segment_patch(patch_data: any) -> dict:
        """
        Runs segmentation on a single patch or extracts metrics from a provided segmentation mask.
        
        Args:
            patch_data: A patch representation (list, dict, or array). If patch_data is a dict
                        containing real mask metrics ('tumor_area_fraction', 'necrosis_area_fraction',
                        'stroma_area_fraction'), those real values are utilized directly.
        """
        # 1. Real mask inputs if provided
        if isinstance(patch_data, dict) and "tumor_area_fraction" in patch_data:
            tumor_frac = float(patch_data["tumor_area_fraction"])
            necrosis_frac = float(patch_data.get("necrosis_area_fraction", 0.0))
            stroma_frac = float(patch_data.get("stroma_area_fraction", 0.0))

            # Strictly validate real mask inputs
            if tumor_frac < 0.0 or necrosis_frac < 0.0 or stroma_frac < 0.0:
                raise ValueError("Compartment area fractions cannot be negative")
            tissue_sum = tumor_frac + necrosis_frac + stroma_frac
            if tissue_sum > 1.0 + 1e-6:
                raise ValueError(f"Sum of compartment area fractions ({tissue_sum:.4f}) exceeds 1.0")

            bg_frac = round(max(0.0, 1.0 - tissue_sum), 4)
            return {
                "mask_coordinates": patch_data.get("mask_coordinates", [0, 0, 256, 256]),
                "tumor_area_fraction": round(tumor_frac, 4),
                "necrosis_area_fraction": round(necrosis_frac, 4),
                "stroma_area_fraction": round(stroma_frac, 4),
                "background_area_fraction": bg_frac,
                "is_mock": False
            }

        # 2. Explicit Mock Mode (Deterministic test harness; NO fake confidence)
        try:
            patch_str = json.dumps(patch_data, sort_keys=True)
        except Exception:
            patch_str = str(patch_data)
        hash_val = int(hashlib.md5(patch_str.encode()).hexdigest(), 16)

        # Strictly partitioned compartment fractions ensuring sum <= 1.0 at all times
        tumor_frac = round((hash_val % 35) / 100.0, 4)             # 0.00 to 0.34
        necrosis_frac = round(((hash_val >> 4) % 15) / 100.0, 4)   # 0.00 to 0.14
        stroma_frac = round(((hash_val >> 8) % 25) / 100.0, 4)     # 0.00 to 0.24
        background_frac = round(1.0 - (tumor_frac + necrosis_frac + stroma_frac), 4)

        return {
            "mask_coordinates": [0, 0, 256, 256],
            "tumor_area_fraction": tumor_frac,
            "necrosis_area_fraction": necrosis_frac,
            "stroma_area_fraction": stroma_frac,
            "background_area_fraction": background_frac,
            "is_mock": True
        }

    @staticmethod
    def segment_slide(patches: list) -> dict:
        """
        Aggregates patch-level segmentations into slide-level metrics.
        """
        total_patches = len(patches)
        tumor_patches = 0
        total_tumor_fraction = 0.0
        total_necrosis_fraction = 0.0
        total_stroma_fraction = 0.0
        is_any_mock = False

        for patch in patches:
            res = TumorSegmentor.segment_patch(patch)
            if res.get("is_mock", False):
                is_any_mock = True
            if res["tumor_area_fraction"] > 0.10:
                tumor_patches += 1
            total_tumor_fraction += res["tumor_area_fraction"]
            total_necrosis_fraction += res.get("necrosis_area_fraction", 0.0)
            total_stroma_fraction += res.get("stroma_area_fraction", 0.0)

        overall_tumor = total_tumor_fraction / total_patches if total_patches > 0 else 0.0
        overall_necrosis = total_necrosis_fraction / total_patches if total_patches > 0 else 0.0
        overall_stroma = total_stroma_fraction / total_patches if total_patches > 0 else 0.0

        return {
            "total_patches": total_patches,
            "tumor_patches": tumor_patches,
            "overall_tumor_fraction": round(overall_tumor, 4),
            "tumor_area_percent": round(overall_tumor * 100.0, 2),
            "necrosis_percent": round(overall_necrosis * 100.0, 2),
            "stroma_percent": round(overall_stroma * 100.0, 2),
            "is_mock": is_any_mock,
            "mask_summary": f"Aggregated from {total_patches} patches" + (" (mock mode)" if is_any_mock else "")
        }

    @staticmethod
    def get_model_info() -> dict:
        """
        Returns model architecture and target class specifications.
        """
        return {
            "model_name": "UNet-ResNet50-Mock",
            "is_mock": True,
            "input_size": 256,
            "num_classes": 4,
            "classes": ["background", "tumor", "stroma", "necrosis"],
            "disclaimer": "Simulated mock segmentor for pipeline testing; real inference requires deployed weights and OpenSlide/GPU backend."
        }
