"""
Digital Biomarker module for PERSEPHONE Response Intelligence Platform.
Computes continuous Digital Biomarker Index (DBI) synthesizing digital histopathology,
radiomics, and kinetic telemetry with research metadata.
"""

class DigitalBiomarkerEngine:
    """
    Evaluates continuous digital phenotypes and computes Digital Biomarker Index (DBI).
    """

    @classmethod
    def compute_digital_biomarker(cls, vector):
        """
        Calculates DBI from MultimodalResponseVector.
        Deterministic for identical inputs.
        """
        purity = vector.get_feature("imaging", "tumor_purity", 70.0)
        necrosis = vector.get_feature("imaging", "necrosis_ratio", 5.0)
        til_density = vector.get_feature("imaging", "til_density", 0.5)
        heterogeneity = vector.get_feature("imaging", "heterogeneity_index", 0.3)
        velocity = vector.get_feature("longitudinal", "volume_velocity", 0.0)

        # Normalized digital spatial score (0.0 to 1.0)
        # Higher purity + higher TIL + lower necrosis + lower heterogeneity = more favorable biology
        norm_purity = min(max(purity / 100.0, 0.0), 1.0)
        norm_necrosis = min(max(necrosis / 20.0, 0.0), 1.0)
        norm_til = min(max(til_density, 0.0), 1.0)
        norm_het = min(max(heterogeneity, 0.0), 1.0)

        spatial_score = (norm_purity * 0.35) + (norm_til * 0.35) + ((1.0 - norm_necrosis) * 0.15) + ((1.0 - norm_het) * 0.15)

        # Kinetic modifier based on velocity
        kinetic_factor = 1.0
        if velocity > 0.05:
            kinetic_factor = 0.85
        elif velocity < -0.05:
            kinetic_factor = 1.15

        raw_dbi = spatial_score * kinetic_factor
        dbi = round(min(max(raw_dbi, 0.0), 1.0), 3)

        confidence = round(
            (vector.imaging.get("tumor_purity").confidence if "tumor_purity" in vector.imaging else 0.8) * 0.6 +
            (vector.imaging.get("til_density").confidence if "til_density" in vector.imaging else 0.8) * 0.4,
            3
        )

        return {
            "name": "Digital Biomarker Index",
            "code": "DBI",
            "value": dbi,
            "confidence": confidence,
            "evidence_basis": [
                f"WSI Tumor Purity: {purity:.1f}%",
                f"TIL Spatial Density: {til_density:.2f}",
                f"Necrosis Fraction: {necrosis:.1f}%",
                f"Radiomic Heterogeneity: {heterogeneity:.2f}"
            ],
            "model_version": "digital-bm-v1",
            "calibration_status": "research",
            "uncertainty": {
                "lower_bound": round(max(0.0, dbi - 0.08), 3),
                "upper_bound": round(min(1.0, dbi + 0.08), 3),
                "ci_level": 0.95
            }
        }
