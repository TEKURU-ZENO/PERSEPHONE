"""
Genomic Biomarker module for PERSEPHONE Response Intelligence Platform.
Extracts genomic susceptibility markers (HRD, TMB, MSI, synthetic lethality) with research metadata.
"""

class GenomicBiomarkerExtractor:
    """
    Evaluates genomic susceptibility metrics from MultimodalResponseVector.
    """

    @classmethod
    def extract_genomic_biomarkers(cls, vector):
        hrd_score = vector.get_feature("genomic", "hrd_score", 42.0)
        tmb = vector.get_feature("genomic", "tmb_mut_per_mb", 8.0)
        msi = vector.get_feature("genomic", "msi_status", "MSS")
        primary_var = vector.get_feature("genomic", "primary_variant", "BRCA1")

        is_hrd_positive = hrd_score >= 42.0 or "BRCA" in str(primary_var).upper()
        is_tmb_high = tmb >= 10.0
        is_msi_high = msi == "MSI-H"

        # Synthetic lethality index (high under HRD+ / BRCA mutations)
        sli = 0.90 if is_hrd_positive else (0.70 if is_tmb_high or is_msi_high else 0.35)

        return {
            "name": "Genomic Biomarker Suite",
            "value": sli,
            "confidence": 0.95,
            "metrics": {
                "hrd_score": float(hrd_score),
                "is_hrd_positive": is_hrd_positive,
                "tmb_mut_per_mb": float(tmb),
                "is_tmb_high": is_tmb_high,
                "msi_status": str(msi),
                "synthetic_lethality_index": round(sli, 3)
            },
            "evidence_basis": [
                f"HRD Score: {hrd_score:.1f} ({'Positive' if is_hrd_positive else 'Negative'})",
                f"TMB: {tmb:.1f} mut/Mb ({'High' if is_tmb_high else 'Normal'})",
                f"MSI Status: {msi}",
                f"Driver Gene: {primary_var}"
            ],
            "model_version": "genomic-bm-v1",
            "calibration_status": "research",
            "uncertainty": {
                "lower_bound": round(max(0.0, sli - 0.05), 3),
                "upper_bound": round(min(1.0, sli + 0.05), 3),
                "ci_level": 0.95
            }
        }
