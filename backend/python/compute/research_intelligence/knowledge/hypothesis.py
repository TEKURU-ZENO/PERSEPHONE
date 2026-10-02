"""
Clinical Hypothesis Generator module for PERSEPHONE Research Intelligence Platform.
Synthesizes mechanistic biological hypotheses connecting Patient -> Mutation -> Pathway -> Drug -> Mechanism.
"""
from typing import Dict, List, Any, Optional


class ClinicalHypothesisGenerator:
    """
    Constructs structured biological mechanisms of action and mechanistic hypotheses.
    """

    @classmethod
    def generate_hypotheses(cls, patient_data: Dict[str, Any], candidate_drugs: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Synthesizes causal biological hypotheses connecting patient alterations to therapeutic vulnerability.
        """
        variants = [str(v).upper() for v in (patient_data.get("variants") or [])]
        hrd_score = float(patient_data.get("hrd_score", 52.0 if any("BRCA" in v for v in variants) else 20.0))
        disease = str(patient_data.get("diagnosis", "")).upper()
        candidates = [d.upper() for d in (candidate_drugs or ["Olaparib", "Niraparib", "Osimertinib", "Adagrasib"])]

        hypotheses = []

        # 1. BRCA1/2 - HRD - PARP Synthetic Lethality
        if any("BRCA" in v for v in variants) or hrd_score >= 42.0:
            if "OLAPARIB" in candidates or "NIRAPARIB" in candidates:
                hypotheses.append({
                    "hypothesis_id": "HYP-BRCA-PARP-01",
                    "variant": "BRCA1/2 Alteration / HRD+",
                    "pathway": "Homologous Recombination DNA Repair",
                    "target": "PARP1 / PARP2",
                    "drug": "Olaparib",
                    "mechanism_type": "Synthetic Lethality",
                    "statement": "BRCA1 deficiency impairs homologous recombination double-strand break repair; inhibition and trapping of PARP1/2 by Olaparib converts unrepaired single-strand breaks into lethal double-strand breaks during replication, triggering selective tumor apoptosis.",
                    "plausibility_score": 0.96,
                    "confidence_tier": "HIGH_CONFIDENCE",
                    "level_of_biological_support": "Robust In Vitro, In Vivo & Phase III Clinical Validation"
                })

        # 2. EGFR Activating - Kinase Blockade
        if any("EGFR" in v for v in variants):
            if "OSIMERTINIB" in candidates:
                hypotheses.append({
                    "hypothesis_id": "HYP-EGFR-TKI-01",
                    "variant": "EGFR L858R / T790M",
                    "pathway": "Receptor Tyrosine Kinase Signaling (PI3K-AKT / MAPK)",
                    "target": "EGFR Kinase Domain",
                    "drug": "Osimertinib",
                    "mechanism_type": "Irreversible Tyrosine Kinase Inhibition",
                    "statement": "Constitutive kinase activation driven by EGFR L858R/T790M stimulates downstream survival pathways; Osimertinib covalently binds C797 in the ATP-binding pocket, shutting down downstream oncogenic signaling.",
                    "plausibility_score": 0.94,
                    "confidence_tier": "HIGH_CONFIDENCE",
                    "level_of_biological_support": "Pivotal Phase III Evidence & Structural Biology"
                })

        # 3. KRAS G12D/C - GTPase Blockade
        if any("KRAS" in v for v in variants):
            if "ADAGRASIB" in candidates:
                hypotheses.append({
                    "hypothesis_id": "HYP-KRAS-GTP-01",
                    "variant": "KRAS G12D/G12C",
                    "pathway": "RAS-RAF-MEK-ERK Mitogenic Cascade",
                    "target": "KRAS G12 Switch-II Pocket",
                    "drug": "Adagrasib",
                    "mechanism_type": "Covalent Allosteric GTPase Lock",
                    "statement": "KRAS mutation traps the GTPase in an active GTP-bound state; Adagrasib locks mutant KRAS in the inactive GDP-bound state, disrupting downstream mitogenic RAF/MEK effector recruitment.",
                    "plausibility_score": 0.91,
                    "confidence_tier": "HIGH_CONFIDENCE",
                    "level_of_biological_support": "Phase I/II Clinical Proof of Concept & Biochemical Assay"
                })

        return hypotheses
