"""
Evidence Extractor module for PERSEPHONE Research Intelligence Platform.
Extracts structured quantitative oncology endpoints and performs orthogonal grading
using Oxford CEBM Levels of Evidence and GRADE rating systems.
"""
from typing import Dict, Any, Optional


class EvidenceExtractor:
    """
    Extracts structured oncology clinical trial endpoints and assigns orthogonal evidence quality ratings.
    """

    @classmethod
    def extract_evidence(cls, paper: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts structured endpoints while preserving orthogonal scientific classifications.
        """
        sample_size = paper.get("sample_size") or paper.get("n", None)
        phase = paper.get("phase", "Preclinical")
        study_design = paper.get("study_design") or cls._infer_study_design(phase, paper.get("title", ""))

        hr_val = paper.get("hazard_ratio")
        hr_lower = paper.get("hr_ci_lower")
        hr_upper = paper.get("hr_ci_upper")

        hr_block = None
        if hr_val is not None:
            hr_block = {
                "value": float(hr_val),
                "lower_bound": float(hr_lower) if hr_lower is not None else round(hr_val * 0.75, 2),
                "upper_bound": float(hr_upper) if hr_upper is not None else round(hr_val * 1.30, 2),
                "ci_level": 0.95,
                "statistically_significant": bool(hr_upper is not None and hr_upper < 1.0)
            }

        pfs_delta = paper.get("median_pfs_delta_months")
        primary_endpoint = paper.get("primary_endpoint_met", True if (hr_val and hr_val < 0.8) else None)

        # Assign Orthogonal Quality Metrics (NEVER collapsed into a single scalar)
        cebm_level = paper.get("cebm_level") or cls._assign_cebm_level(study_design, phase)
        grade_rating = paper.get("grade_rating") or cls._assign_grade_rating(cebm_level, sample_size, hr_block)

        return {
            "evidence_id": f"evd-{paper.get('pmid', 'gen')}",
            "study_design": study_design,
            "phase": phase,
            "sample_size": sample_size,
            "hazard_ratio": hr_block,
            "median_pfs_delta_months": pfs_delta,
            "primary_endpoint_met": primary_endpoint,
            "quality_grading": {
                "cebm_level": cebm_level,
                "grade_rating": grade_rating,
                "risk_of_bias": paper.get("risk_of_bias", "Low" if "Phase III" in phase else "Moderate")
            }
        }

    @staticmethod
    def _infer_study_design(phase: str, title: str) -> str:
        phase_up = phase.upper()
        title_up = title.upper()
        if "PHASE III" in phase_up or "PHASE 3" in phase_up or "RANDOMIZED" in title_up:
            return "Phase III Double-Blind Randomized Controlled Trial"
        elif "PHASE II" in phase_up or "PHASE 2" in phase_up:
            return "Phase II Single-Arm Interventional Study"
        elif "META-ANALYSIS" in title_up:
            return "Systematic Review & Meta-Analysis"
        elif "OBSERVATIONAL" in title_up or "REGISTRY" in title_up:
            return "Real-World Observational Cohort Study"
        return "Translational & Preclinical Study"

    @staticmethod
    def _assign_cebm_level(study_design: str, phase: str) -> str:
        """
        Oxford Centre for Evidence-Based Medicine (CEBM) 2011 Levels:
        Level 1a: Systematic review of RCTs
        Level 1b: Individual randomized controlled trial with narrow CI
        Level 2a: Systematic review of cohort studies
        Level 2b: Individual cohort study or low-quality RCT
        Level 3: Case-control study
        Level 4: Case-series
        Level 5: Expert opinion / bench mechanism without explicit critical appraisal
        """
        if "Meta-Analysis" in study_design:
            return "Level 1a"
        elif "Phase III" in study_design or "Phase III" in phase:
            return "Level 1b"
        elif "Phase II" in study_design or "Phase II" in phase:
            return "Level 2b"
        elif "Observational" in study_design or "Cohort" in study_design:
            return "Level 2b"
        return "Level 5"

    @staticmethod
    def _assign_grade_rating(cebm_level: str, sample_size: Optional[int], hr_block: Optional[Dict[str, Any]]) -> str:
        """
        GRADE System: High, Moderate, Low, Very Low.
        """
        if cebm_level in ["Level 1a", "Level 1b"] and (sample_size is None or sample_size >= 200):
            if hr_block and hr_block.get("statistically_significant", False):
                return "High"
            return "Moderate"
        elif cebm_level in ["Level 1b", "Level 2a", "Level 2b"]:
            return "Moderate"
        elif cebm_level in ["Level 3", "Level 4"]:
            return "Low"
        return "Very Low"
