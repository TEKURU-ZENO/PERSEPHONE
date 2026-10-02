"""
ESMO Guideline reference source registry for PERSEPHONE Research Intelligence Platform.
"""
from backend.python.compute.research_intelligence.guidelines.schemas import GuidelineReference, DecisionRule

ESMO_DECISION_RULES = [
    DecisionRule(
        rule_id="ESMO-OV-001",
        disease="Ovarian Cancer",
        stage=["Stage III", "Stage IV"],
        biomarker_requirements={"BRCA": "mutated", "HRD": "positive"},
        treatment_line="First-line Maintenance",
        recommended_drug="Olaparib",
        reference=GuidelineReference(
            reference_id="REF-ESMO-OV-2025-1",
            organization="ESMO",
            guideline_title="Newly Diagnosed and Recurrent Epithelial Ovarian Cancer: ESMO Clinical Practice Guidelines",
            version="2025 Edition",
            publication_date="2025-09-01",
            section="First-line Management: Maintenance Strategies",
            recommendation_id="ESMO-MCBS-5",
            evidence_category="Category 1", # ESMO MCBS Level 1A
            preference_tier="Preferred",
            source_url="https://www.annalsofoncology.org/article/S0923-7534(19)31174-8/fulltext",
            effective_from="2025-09-01"
        ),
        rationale="ESMO Clinical Practice Guidelines recommend maintenance Olaparib in BRCA1/2-mutated and HRD-positive advanced ovarian cancer patients responding to platinum, supported by ESMO-MCBS score 5."
    )
]
