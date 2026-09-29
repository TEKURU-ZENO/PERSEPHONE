"""
Multimodal Response Classifier module for PERSEPHONE Response Intelligence Platform.
Classifies concordance across radiologic, serum, and liquid biopsy response streams.
"""

class MultimodalResponseClassifier:
    """
    Classifies multimodal treatment response concordance.
    """

    @classmethod
    def classify_response(cls, vector):
        vel = vector.get_feature("longitudinal", "volume_velocity", 0.0)
        vaf = vector.get_feature("longitudinal", "ctdna_vaf_pct", 1.0)
        til = vector.get_feature("imaging", "til_density", 0.5)

        # Molecular signal vs Radiologic signal
        is_imaging_progressing = vel > 0.05
        is_imaging_shrinking = vel < -0.05
        is_molecular_progressing = vaf > 2.0

        if is_imaging_shrinking and not is_molecular_progressing:
            category = "Concordant Response"
            description = "Radiologic tumor regression concordant with suppressed ctDNA burden."
            concordance_score = 0.95
        elif is_imaging_progressing and is_molecular_progressing:
            category = "Concordant Progression"
            description = "Bi-modal progression confirmed across volumetric CT and liquid biopsy ctDNA."
            concordance_score = 0.92
        elif not is_imaging_progressing and is_molecular_progressing:
            category = "Molecular-Only Progression"
            description = "Early subclonal expansion detected in liquid biopsy prior to radiologic enlargement."
            concordance_score = 0.85
        elif is_imaging_progressing and not is_molecular_progressing:
            category = "Dissociated Response"
            description = "Radiologic lesion enlargement without proportional systemic ctDNA elevation."
            concordance_score = 0.70
        else:
            category = "Stable Disease"
            description = "Controlled volumetric and molecular dynamics on active regimen."
            concordance_score = 0.88

        return {
            "name": "Multimodal Response Concordance",
            "category": category,
            "concordance_score": concordance_score,
            "description": description,
            "features": {
                "volume_velocity": vel,
                "ctdna_vaf_pct": vaf,
                "til_density": til
            },
            "evidence_basis": [
                f"Volume velocity: {vel:+.2f} cm³/day",
                f"ctDNA VAF: {vaf:.1f}%",
                f"Classification: {category}"
            ],
            "model_version": "response-classifier-v1",
            "calibration_status": "research"
        }
