"""
Contraindications Module for PERSEPHONE Governance Platform.
Evaluates pharmacogenomic, clinical, and drug-disease contraindications
backed by versioned CPIC (Clinical Pharmacogenetics Implementation Consortium)
and FDA Boxed Warning registries.
"""
from typing import Dict, List, Any, Optional

CONTRAINDICATION_REGISTRY = {
    "CPIC_DPYD_5FU": {
        "rule_id": "CONTRA-DPYD-001",
        "authority": "CPIC Guideline for Fluoropyrimidines and DPYD (2023 Update)",
        "version": "v2023.1",
        "drug_targets": ["5-FU", "FLUOROURACIL", "CAPECITABINE"],
        "variant_triggers": ["DPYD *2A", "DPYD *13", "DPYD C.2846A>T", "DPYD HAP B3"],
        "severity": "CRITICAL",
        "action": "ABSOLUTE_CONTRAINDICATION",
        "rationale": "Complete or severe DPD deficiency causes life-threatening, lethal mucositis, neutropenia, and neurotoxicity with fluoropyrimidines."
    },
    "CPIC_UGT1A1_IRINOTECAN": {
        "rule_id": "CONTRA-UGT1A1-001",
        "authority": "CPIC Guideline for Irinotecan and UGT1A1",
        "version": "v2022.1",
        "drug_targets": ["IRINOTECAN", "ONIVYDE"],
        "variant_triggers": ["UGT1A1*28", "UGT1A1*6"],
        "severity": "HIGH",
        "action": "DOSE_REDUCTION_OR_AVOIDANCE",
        "rationale": "Homozygous UGT1A1*28 (*28/*28) dramatically impairs SN-38 glucuronidation; high risk of severe Grade 4 neutropenia and diarrhea."
    },
    "BEVACIZUMAB_BOWEL_PERFORATION": {
        "rule_id": "CONTRA-BEV-001",
        "authority": "FDA Boxed Warning / NCCN Ovarian Panel Safety Alert",
        "version": "v2024.1",
        "drug_targets": ["BEVACIZUMAB", "AVASTIN"],
        "clinical_triggers": ["BOWEL_OBSTRUCTION", "BOWEL_PERFORATION_HISTORY", "BOWEL_WALL_INVOLVEMENT"],
        "severity": "CRITICAL",
        "action": "ABSOLUTE_CONTRAINDICATION",
        "rationale": "Bevacizumab is strictly contraindicated in patients with signs or symptoms of bowel obstruction or transmural tumor involvement due to catastrophic gastrointestinal perforation."
    },
    "EGFR_TKI_INTERSTITIAL_LUNG_DISEASE": {
        "rule_id": "CONTRA-EGFR-001",
        "authority": "FDA Labeling for Osimertinib / ASCO Thoracic Oncology",
        "version": "v2023.1",
        "drug_targets": ["OSIMERTINIB", "ERLOTINIB", "GEFITINIB"],
        "clinical_triggers": ["INTERSTITIAL_LUNG_DISEASE", "PULMONARY_FIBROSIS", "ACTIVE_PNEUMONITIS"],
        "severity": "CRITICAL",
        "action": "PERMANENT_DISCONTINUATION_REQUIRED",
        "rationale": "Pre-existing ILD or drug-induced pneumonitis carries high fatality rate under third-generation EGFR-TKIs."
    }
}


class ContraindicationsEvaluator:
    """
    Evaluates patient molecular profile and clinical conditions for drug-specific contraindications.
    """

    @classmethod
    def evaluate_contraindications(
        cls,
        patient_data: Dict[str, Any],
        proposed_drug: str
    ) -> Dict[str, Any]:
        drug_up = proposed_drug.strip().upper()
        variants = [str(v).upper() for v in (patient_data.get("variants") or [])]
        conditions = [str(c).upper() for c in (patient_data.get("conditions") or patient_data.get("comorbidities") or [])]
        clinical_history = [str(h).upper() for h in (patient_data.get("clinical_history") or [])]
        all_signals = set(conditions + clinical_history)

        detected_contraindications = []
        rule_versions_applied = []

        for cid, spec in CONTRAINDICATION_REGISTRY.items():
            rule_versions_applied.append(f"{spec['rule_id']}:{spec['version']}")

            # Check drug target match
            if not any(t in drug_up for t in spec["drug_targets"]):
                continue

            # Check genomic variant triggers
            triggered_variants = [v for v in spec.get("variant_triggers", []) if any(v in pat_v for pat_v in variants)]
            if triggered_variants:
                detected_contraindications.append({
                    "rule_id": spec["rule_id"],
                    "authority": spec["authority"],
                    "version": spec["version"],
                    "severity": spec["severity"],
                    "trigger_type": "GENOMIC_PHARMACOGENETIC",
                    "trigger_detail": triggered_variants,
                    "action": spec["action"],
                    "rationale": spec["rationale"]
                })

            # Check clinical condition triggers
            triggered_conditions = [c for c in spec.get("clinical_triggers", []) if c in all_signals]
            if triggered_conditions:
                detected_contraindications.append({
                    "rule_id": spec["rule_id"],
                    "authority": spec["authority"],
                    "version": spec["version"],
                    "severity": spec["severity"],
                    "trigger_type": "CLINICAL_COMORBIDITY",
                    "trigger_detail": triggered_conditions,
                    "action": spec["action"],
                    "rationale": spec["rationale"]
                })

        has_critical = any(c["severity"] == "CRITICAL" for c in detected_contraindications)
        status = "CONTRAINDICATED" if has_critical else ("CAUTION" if detected_contraindications else "CLEARED")

        return {
            "status": status,
            "has_contraindications": len(detected_contraindications) > 0,
            "contraindications_count": len(detected_contraindications),
            "contraindications": detected_contraindications,
            "rule_versions_applied": rule_versions_applied,
            "cleared_for_therapy": not has_critical
        }
