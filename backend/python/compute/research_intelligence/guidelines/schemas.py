"""
Guideline schemas module for PERSEPHONE Research Intelligence Platform.
Defines typed models for GuidelineReference, DecisionRule, and RecommendationCategory.
"""
from typing import Dict, List, Optional, Any


class GuidelineReference:
    """
    Metadata representation of a clinical guideline reference adhering to copyright and licensing constraints.
    Stores authoritative citation, section, and version metadata without scraping full copyrighted text.
    """
    def __init__(
        self,
        reference_id: str,
        organization: str, # NCCN, ASCO, ESMO
        guideline_title: str,
        version: str,
        publication_date: str,
        section: str,
        recommendation_id: str,
        evidence_category: Optional[str] = None, # Category 1, Category 2A, Category 2B, Category 3
        preference_tier: Optional[str] = None,   # Preferred, Other Recommended, Useful in Certain Circumstances
        source_url: str = "",
        effective_from: str = "",
        effective_until: Optional[str] = None,
        superseded_by: Optional[str] = None
    ):
        self.reference_id = reference_id
        self.organization = organization
        self.guideline_title = guideline_title
        self.version = version
        self.publication_date = publication_date
        self.section = section
        self.recommendation_id = recommendation_id
        self.evidence_category = evidence_category
        self.preference_tier = preference_tier
        self.source_url = source_url
        self.effective_from = effective_from
        self.effective_until = effective_until
        self.superseded_by = superseded_by

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reference_id": self.reference_id,
            "organization": self.organization,
            "guideline_title": self.guideline_title,
            "version": self.version,
            "publication_date": self.publication_date,
            "section": self.section,
            "recommendation_id": self.recommendation_id,
            "evidence_category": self.evidence_category,
            "preference_tier": self.preference_tier,
            "source_url": self.source_url,
            "effective_from": self.effective_from,
            "effective_until": self.effective_until,
            "superseded_by": self.superseded_by,
            "is_current": self.superseded_by is None
        }


class DecisionRule:
    """
    Defines a structured patient matching criteria for a clinical guideline recommendation.
    """
    def __init__(
        self,
        rule_id: str,
        disease: str,
        stage: List[str],
        biomarker_requirements: Dict[str, Any], # e.g. {"BRCA1": "mutated", "HRD": "positive"}
        treatment_line: str,                    # First-line maintenance, Second-line, Recurrent
        recommended_drug: str,
        reference: GuidelineReference,
        rationale: str
    ):
        self.rule_id = rule_id
        self.disease = disease
        self.stage = stage
        self.biomarker_requirements = biomarker_requirements
        self.treatment_line = treatment_line
        self.recommended_drug = recommended_drug
        self.reference = reference
        self.rationale = rationale

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "disease": self.disease,
            "stage": self.stage,
            "biomarker_requirements": self.biomarker_requirements,
            "treatment_line": self.treatment_line,
            "recommended_drug": self.recommended_drug,
            "reference": self.reference.to_dict(),
            "rationale": self.rationale
        }
