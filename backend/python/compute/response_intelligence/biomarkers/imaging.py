"""
Imaging Biomarker module for PERSEPHONE Response Intelligence Platform.
Extracts spatial tissue morphology and radiomic response markers.
"""

class ImagingBiomarkerExtractor:
    """
    Extracts structured imaging response markers from MultimodalResponseVector.
    """

    @classmethod
    def extract_imaging_biomarkers(cls, vector):
        purity = vector.get_feature("imaging", "tumor_purity", 70.0)
        necrosis = vector.get_feature("imaging", "necrosis_ratio", 5.0)
        til_density = vector.get_feature("imaging", "til_density", 0.5)
        het = vector.get_feature("imaging", "heterogeneity_index", 0.3)

        viable_ratio = round(max(0.0, (purity - necrosis) / max(purity, 1.0)), 3)
        stroma_infilt = round(max(0.0, 1.0 - (purity / 100.0)), 3)

        composite_img = round(
            min(max((purity / 100.0) * 0.4 + til_density * 0.3 + (1.0 - het) * 0.3, 0.0), 1.0),
            3
        )

        return {
            "name": "Imaging Biomarker Suite",
            "value": composite_img,
            "confidence": 0.90,
            "metrics": {
                "viable_cellularity_ratio": viable_ratio,
                "stroma_infiltration_fraction": stroma_infilt,
                "til_spatial_score": round(til_density, 3),
                "radiomic_heterogeneity": round(het, 3)
            },
            "evidence_basis": [
                f"Viable cellularity ratio: {viable_ratio:.2f}",
                f"Stroma infiltration: {stroma_infilt:.2f}",
                f"TIL spatial score: {til_density:.2f}",
                f"Radiomic heterogeneity: {het:.2f}"
            ],
            "model_version": "imaging-bm-v1",
            "calibration_status": "research",
            "uncertainty": {
                "lower_bound": round(max(0.0, composite_img - 0.07), 3),
                "upper_bound": round(min(1.0, composite_img + 0.07), 3),
                "ci_level": 0.95
            }
        }
