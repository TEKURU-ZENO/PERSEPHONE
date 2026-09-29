"""
Resistance Mechanism Detector module for PERSEPHONE Response Intelligence Platform.
Identifies active and emerging molecular and phenotypic drug resistance mechanisms.
"""

class ResistanceMechanismDetector:
    """
    Detects secondary mutations, bypass pathway activations, and phenotypic resistance mechanisms.
    """

    @classmethod
    def detect_mechanisms(cls, vector):
        primary_var = vector.get_feature("genomic", "primary_variant", "BRCA1")
        vaf = vector.get_feature("longitudinal", "ctdna_vaf_pct", 1.0)
        vel = vector.get_feature("longitudinal", "volume_velocity", 0.0)
        necrosis = vector.get_feature("imaging", "necrosis_ratio", 5.0)
        candidate_drug = vector.get_feature("pharmacologic", "candidate_drug", "Olaparib")

        detected = []

        # 1. Secondary reversion mutation detection (PARP / Platinum in BRCA1/2)
        if "BRCA" in str(primary_var).upper() and vaf >= 3.0:
            detected.append({
                "mechanism_type": "Secondary Reversion Mutation",
                "gene": "BRCA1",
                "description": "Secondary somatic in-frame reversion restoring homologous recombination repair proficiency.",
                "affected_drugs": ["Olaparib", "Talazoparib", "Carboplatin"],
                "evidence_level": "Tier I-B",
                "detection_source": "ctDNA Liquid Biopsy Clonal Tracking"
            })

        # 2. Bypass signaling pathway activation
        if vel > 0.05 and necrosis > 6.0:
            detected.append({
                "mechanism_type": "Bypass Signaling Activation",
                "gene": "PI3K/AKT/mTOR",
                "description": "Compensatory upstream PI3K/mTOR pathway activation driving survival under PARP blockade.",
                "affected_drugs": [candidate_drug],
                "evidence_level": "Tier II-C",
                "detection_source": "Radiomic Growth Kinetics & Cell Viability"
            })

        # 3. Target alteration / gatekeeper
        if "EGFR" in str(primary_var).upper() and vaf >= 2.0:
            detected.append({
                "mechanism_type": "Gatekeeper Mutation",
                "gene": "EGFR",
                "description": "Acquired T790M or C797S gatekeeper mutation impairing small-molecule kinase binding.",
                "affected_drugs": ["Gefitinib", "Erlotinib", "Osimertinib"],
                "evidence_level": "Tier I-A",
                "detection_source": "Targeted Variant Annotation"
            })

        # Determine resistance state
        if len(detected) >= 2 or (detected and vel > 0.05):
            state = "Acquired Resistance"
        elif detected:
            state = "Emerging Subclonal Resistance"
        else:
            state = "Sensitive / No Active Resistance Detected"

        return {
            "name": "Resistance Mechanism Analysis",
            "state": state,
            "has_active_resistance": bool(detected),
            "detected_mechanisms_count": len(detected),
            "mechanisms": detected,
            "model_version": "resistance-detector-v1",
            "calibration_status": "research"
        }
