"""
ASCO Guideline reference source registry for PERSEPHONE Research Intelligence Platform.
"""
from backend.python.compute.research_intelligence.guidelines.schemas import GuidelineReference, DecisionRule

ASCO_DECISION_RULES = [
    DecisionRule(
        rule_id="ASCO-OV-001",
        disease="Ovarian Cancer",
        stage=["Stage III", "Stage IV"],
        biomarker_requirements={"BRCA": "mutated"},
        treatment_line="First-line Maintenance",
        recommended_drug="Olaparib",
        reference=GuidelineReference(
            reference_id="REF-ASCO-OV-2025-1",
            organization="ASCO",
            guideline_title="PARP Inhibitors in the Management of Ovarian Cancer: ASCO Guideline",
            version="2025 Update",
            publication_date="2025-06-10",
            section="Maintenance Therapy: Primary Stage III-IV Epithelial Ovarian Cancer",
            recommendation_id="ASCO-REC-1.1",
            evidence_category="Category 1",
            preference_tier="Preferred",
            source_url="https://ascopubs.org/doi/full/10.1200/JCO.20.01924",
            effective_from="2025-06-10"
        ),
        rationale="ASCO recommends that patients with newly diagnosed stage III-IV ovarian cancer and a germline or somatic BRCA1/2 mutation who achieve PR/CR to platinum-based chemotherapy should be offered maintenance Olaparib."
    )
]
