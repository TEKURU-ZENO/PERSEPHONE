"""
NCCN Guideline reference source registry for PERSEPHONE Research Intelligence Platform.
Stores version-aware NCCN decision rules and Category 1/2A recommendation references.
"""
from backend.python.compute.research_intelligence.guidelines.schemas import GuidelineReference, DecisionRule

NCCN_DECISION_RULES = [
    DecisionRule(
        rule_id="NCCN-OV-001",
        disease="Ovarian Cancer",
        stage=["Stage III", "Stage IV"],
        biomarker_requirements={"BRCA": "mutated", "HRD": "positive"},
        treatment_line="First-line Maintenance",
        recommended_drug="Olaparib",
        reference=GuidelineReference(
            reference_id="REF-NCCN-OV-2026-1",
            organization="NCCN",
            guideline_title="NCCN Clinical Practice Guidelines in Oncology: Ovarian Cancer",
            version="Version 1.2026",
            publication_date="2026-01-15",
            section="Principles of Systemic Therapy: Maintenance Therapy for Stage III-IV",
            recommendation_id="OV-MAINT-BRCA-CAT1",
            evidence_category="Category 1",
            preference_tier="Preferred",
            source_url="https://www.nccn.org/guidelines/guidelines-detail?category=1&id=1453",
            effective_from="2026-01-15"
        ),
        rationale="Category 1 recommendation for Olaparib monotherapy maintenance in patients with deleterious germline or somatic BRCA1/2 mutations following partial or complete response to first-line platinum-based chemotherapy based on SOLO-1 trial."
    ),
    DecisionRule(
        rule_id="NCCN-OV-002",
        disease="Ovarian Cancer",
        stage=["Stage III", "Stage IV"],
        biomarker_requirements={"HRD": "positive"},
        treatment_line="First-line Maintenance",
        recommended_drug="Niraparib",
        reference=GuidelineReference(
            reference_id="REF-NCCN-OV-2026-2",
            organization="NCCN",
            guideline_title="NCCN Clinical Practice Guidelines in Oncology: Ovarian Cancer",
            version="Version 1.2026",
            publication_date="2026-01-15",
            section="Principles of Systemic Therapy: Maintenance Therapy for Stage III-IV",
            recommendation_id="OV-MAINT-HRD-CAT1",
            evidence_category="Category 1",
            preference_tier="Preferred",
            source_url="https://www.nccn.org/guidelines/guidelines-detail?category=1&id=1453",
            effective_from="2026-01-15"
        ),
        rationale="Category 1 recommendation for Niraparib monotherapy maintenance in patients with newly diagnosed advanced ovarian cancer who responded to platinum chemotherapy, irrespective of BRCA mutation status (PRIMA trial)."
    ),
    DecisionRule(
        rule_id="NCCN-NSCLC-001",
        disease="Non-Small Cell Lung Cancer",
        stage=["Stage III", "Stage IV"],
        biomarker_requirements={"EGFR": "mutated"},
        treatment_line="First-line",
        recommended_drug="Osimertinib",
        reference=GuidelineReference(
            reference_id="REF-NCCN-NSCLC-2026-1",
            organization="NCCN",
            guideline_title="NCCN Guidelines for Non-Small Cell Lung Cancer",
            version="Version 2.2026",
            publication_date="2026-02-01",
            section="EGFR Mutation-Positive Advanced or Metastatic NSCLC",
            recommendation_id="NSCLC-EGFR-CAT1",
            evidence_category="Category 1",
            preference_tier="Preferred",
            source_url="https://www.nccn.org/guidelines/guidelines-detail?category=1&id=1449",
            effective_from="2026-02-01"
        ),
        rationale="Category 1 preferred first-line therapy for sensitizing EGFR mutations (exon 19 deletion, exon 21 L858R) based on superior overall survival in the FLAURA trial."
    ),
    DecisionRule(
        rule_id="NCCN-CRC-001",
        disease="Colorectal Cancer",
        stage=["Stage IV"],
        biomarker_requirements={"KRAS": "mutated"},
        treatment_line="First-line / Maintenance",
        recommended_drug="FOLFIRI + Bevacizumab",
        reference=GuidelineReference(
            reference_id="REF-NCCN-CRC-2026-1",
            organization="NCCN",
            guideline_title="NCCN Guidelines for Colon Cancer",
            version="Version 1.2026",
            publication_date="2026-01-20",
            section="Systemic Therapy for Advanced or Metastatic Disease: RAS-Mutant",
            recommendation_id="CRC-RAS-DOUBLET-BEV",
            evidence_category="Category 1",
            preference_tier="Preferred",
            source_url="https://www.nccn.org/guidelines/guidelines-detail?category=1&id=1428",
            effective_from="2026-01-20"
        ),
        rationale="In metastatic colorectal cancer with RAS mutation (KRAS/NRAS codon 12, 13, 61, 117, 146), anti-EGFR therapies (cetuximab, panitumumab) are contraindicated. Standard therapy is doublet chemotherapy (FOLFOX, FOLFIRI, or CAPEOX) ± bevacizumab. KRAS G12D has no FDA-approved targeted inhibitor; patients should continue systemic chemotherapy or consider clinical trials. Adagrasib + cetuximab is Category 2A strictly for KRAS G12C only."
    )
]
