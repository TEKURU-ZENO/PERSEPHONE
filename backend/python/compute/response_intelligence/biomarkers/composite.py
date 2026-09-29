"""
Composite Biomarker module for PERSEPHONE Response Intelligence Platform.
Fuses digital, imaging, genomic, and pharmacogenomic signals into an integrated
Composite Actionability Score (CAS) with explicit research metadata.
"""
from backend.python.compute.response_intelligence.biomarkers.digital import DigitalBiomarkerEngine
from backend.python.compute.response_intelligence.biomarkers.imaging import ImagingBiomarkerExtractor
from backend.python.compute.response_intelligence.biomarkers.genomic import GenomicBiomarkerExtractor

class CompositeBiomarkerSynthesizer:
    """
    Synthesizes multimodal biomarkers into an integrated actionability score.
    """

    @classmethod
    def synthesize_composite(cls, vector):
        digital_res = DigitalBiomarkerEngine.compute_digital_biomarker(vector)
        imaging_res = ImagingBiomarkerExtractor.extract_imaging_biomarkers(vector)
        genomic_res = GenomicBiomarkerExtractor.extract_genomic_biomarkers(vector)

        # Pharmacologic sensitivity contribution
        ic50 = vector.get_feature("pharmacologic", "predicted_ic50_um", 2.5)
        # Lower IC50 = higher sensitivity score
        pharma_score = min(max(1.0 - (ic50 / 10.0), 0.0), 1.0)

        # Composite Actionability Score (CAS)
        # Genomic 40% + Imaging 25% + Digital 20% + Pharma 15%
        cas = (
            genomic_res["value"] * 0.40 +
            imaging_res["value"] * 0.25 +
            digital_res["value"] * 0.20 +
            pharma_score * 0.15
        )
        cas = round(min(max(cas, 0.0), 1.0), 3)

        if cas >= 0.75:
            tier = "Highly Favorable"
        elif cas >= 0.55:
            tier = "Favorable"
        elif cas >= 0.35:
            tier = "Intermediate"
        else:
            tier = "Unfavorable"

        confidence = round(
            genomic_res["confidence"] * 0.40 +
            imaging_res["confidence"] * 0.25 +
            digital_res["confidence"] * 0.20 +
            0.85 * 0.15,
            3
        )

        return {
            "name": "Composite Actionability Score",
            "code": "CAS",
            "value": cas,
            "response_likelihood_tier": tier,
            "confidence": confidence,
            "sub_scores": {
                "genomic_score": genomic_res["value"],
                "imaging_score": imaging_res["value"],
                "digital_biomarker_index": digital_res["value"],
                "pharmacologic_score": round(pharma_score, 3)
            },
            "evidence_basis": (
                genomic_res["evidence_basis"][:2] +
                imaging_res["evidence_basis"][:2] +
                digital_res["evidence_basis"][:1]
            ),
            "model_version": "composite-bm-v1",
            "calibration_status": "research",
            "uncertainty": {
                "lower_bound": round(max(0.0, cas - 0.06), 3),
                "upper_bound": round(min(1.0, cas + 0.06), 3),
                "ci_level": 0.95
            }
        }
