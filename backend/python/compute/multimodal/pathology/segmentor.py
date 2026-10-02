import hashlib
import json

class TumorSegmentor:
    """
    Clinical/Scientific Purpose:
    Segments key tissue compartments (tumor, stroma, necrosis, background) within H&E stained 
    slides. This serves as the foundation for automated computational biomarker extraction 
    (e.g., Tumor-Stroma Ratio).
    """

    @staticmethod
    def segment_patch(patch_data: list) -> dict:
        """
        Runs segmentation on a single patch.
        Uses deterministic mock segmentation based on a hash of the patch content.
        """
        # Create deterministic pseudo-random variables based on patch content
        patch_str = json.dumps(patch_data, sort_keys=True)
        hash_val = int(hashlib.md5(patch_str.encode()).hexdigest(), 16)
        
        tumor_frac = (hash_val % 60) / 100.0
        necrosis_frac = ((hash_val >> 4) % 15) / 100.0
        stroma_frac = ((hash_val >> 8) % 30) / 100.0
        confidence = 0.70 + ((hash_val % 30) / 100.0)
        
        return {
            "mask_coordinates": [0, 0, 256, 256],
            "tumor_area_fraction": tumor_frac,
            "necrosis_area_fraction": necrosis_frac,
            "stroma_area_fraction": stroma_frac,
            "confidence": confidence
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
        
        for patch in patches:
            res = TumorSegmentor.segment_patch(patch)
            if res["tumor_area_fraction"] > 0.1:
                tumor_patches += 1
            total_tumor_fraction += res["tumor_area_fraction"]
            total_necrosis_fraction += res.get("necrosis_area_fraction", 0.0)
            total_stroma_fraction += res.get("stroma_area_fraction", 0.0)
            
        overall_fraction = total_tumor_fraction / total_patches if total_patches > 0 else 0.0
        overall_necrosis = total_necrosis_fraction / total_patches if total_patches > 0 else 0.0
        overall_stroma = total_stroma_fraction / total_patches if total_patches > 0 else 0.0
        
        return {
            "total_patches": total_patches,
            "tumor_patches": tumor_patches,
            "overall_tumor_fraction": round(overall_fraction, 4),
            "tumor_purity_percent": round(overall_fraction * 100.0, 2),
            "necrosis_percent": round(overall_necrosis * 100.0, 2),
            "stroma_percent": round(overall_stroma * 100.0, 2),
            "mask_summary": f"Aggregated from {total_patches} patches"
        }

    @staticmethod
    def get_model_info() -> dict:
        """
        Returns model architecture and target class specifications.
        """
        return {
            "model_name": "UNet-ResNet50",
            "input_size": 256,
            "num_classes": 3,
            "classes": ["background", "tumor", "stroma"]
        }
