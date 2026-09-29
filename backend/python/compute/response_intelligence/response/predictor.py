"""
Treatment Response Predictor module for PERSEPHONE Response Intelligence Platform.
Implements research/simulation predictive models for ORR, DCR, and PFS
with mandatory research governance calibration metadata.
"""

class TreatmentResponsePredictor:
    """
    Predicts efficacy metrics for candidate therapeutic regimens under multimodal evidence.
    """

    @classmethod
    def predict_response(cls, vector, proposed_drug="Olaparib"):
        """
        Computes response predictions with mandatory research calibration metadata.
        All probabilities are strictly bounded in [0, 1]; PFS is non-negative.
        """
        primary_var = vector.get_feature("genomic", "primary_variant", "BRCA1")
        hrd_score = vector.get_feature("genomic", "hrd_score", 42.0)
        til_density = vector.get_feature("imaging", "til_density", 0.5)
        synergy = vector.get_feature("pharmacologic", "synergy_score", 0.70)
        ic50 = vector.get_feature("pharmacologic", "predicted_ic50_um", 2.0)
        velocity = vector.get_feature("longitudinal", "volume_velocity", 0.0)

        drug_name = proposed_drug or vector.get_feature("pharmacologic", "candidate_drug", "Olaparib")

        # Base response affinity based on synthetic lethality
        is_parp = "olaparib" in drug_name.lower() or "talazoparib" in drug_name.lower()
        is_hrd = hrd_score >= 42.0 or "BRCA" in str(primary_var).upper()

        if is_parp and is_hrd:
            base_orr = 0.75
            base_pfs = 330.0
            depth_pct = -65.0
        elif is_parp and not is_hrd:
            base_orr = 0.30
            base_pfs = 140.0
            depth_pct = -20.0
        else:
            base_orr = 0.55
            base_pfs = 210.0
            depth_pct = -45.0

        # Modulation by TILs and IC50
        til_mod = (til_density - 0.5) * 0.15
        ic50_mod = max(-0.15, min(0.15, (3.0 - ic50) * 0.05))
        syn_mod = (synergy - 0.5) * 0.10

        # Calculate final bounded ORR and DCR
        raw_orr = base_orr + til_mod + ic50_mod + syn_mod
        orr = round(max(0.05, min(0.95, raw_orr)), 3)
        dcr = round(max(orr, min(0.98, orr + 0.18)), 3)

        # Calculate bounded PFS (strictly non-negative)
        kinetic_pen = 45.0 if velocity > 0.08 else 0.0
        pfs_days = round(max(30.0, base_pfs + (til_mod * 80.0) + (syn_mod * 60.0) - kinetic_pen), 1)

        predicted_depth = round(min(0.0, max(-95.0, depth_pct + (til_mod * 20.0))), 1)

        # Evidence basis documentation
        evidence_basis = [
            f"Target drug: {drug_name}",
            f"Genomic context: {primary_var} (HRD score: {hrd_score:.1f})",
            f"In vitro IC50: {ic50:.2f} µM with synergy score: {synergy:.2f}",
            f"TIL spatial density: {til_density:.2f}"
        ]

        # Model confidence reflects vector completeness
        missing_ratio = vector.provenance.get("missingness_ratio", 0.0)
        confidence = round(max(0.60, min(0.95, 0.90 - (missing_ratio * 0.3))), 3)

        return {
            "drug_evaluated": drug_name,
            "predicted_orr": {
                "value": orr,
                "confidence": confidence,
                "evidence_basis": evidence_basis,
                "model_version": "response-v1",
                "calibration_status": "research",
                "uncertainty": {
                    "lower_bound": round(max(0.0, orr - 0.08), 3),
                    "upper_bound": round(min(1.0, orr + 0.08), 3),
                    "ci_level": 0.95
                }
            },
            "predicted_dcr": {
                "value": dcr,
                "confidence": confidence,
                "evidence_basis": evidence_basis,
                "model_version": "response-v1",
                "calibration_status": "research",
                "uncertainty": {
                    "lower_bound": round(max(0.0, dcr - 0.06), 3),
                    "upper_bound": round(min(1.0, dcr + 0.06), 3),
                    "ci_level": 0.95
                }
            },
            "predicted_pfs_days": {
                "value": pfs_days,
                "confidence": confidence,
                "evidence_basis": evidence_basis,
                "model_version": "response-v1",
                "calibration_status": "research",
                "uncertainty": {
                    "lower_bound": round(max(0.0, pfs_days - 35.0), 1),
                    "upper_bound": round(pfs_days + 45.0, 1),
                    "ci_level": 0.95
                }
            },
            "predicted_depth_of_response": {
                "value": predicted_depth,
                "confidence": confidence,
                "evidence_basis": evidence_basis,
                "model_version": "response-v1",
                "calibration_status": "research",
                "uncertainty": {
                    "lower_bound": round(predicted_depth - 10.0, 1),
                    "upper_bound": round(min(0.0, predicted_depth + 10.0), 1),
                    "ci_level": 0.95
                }
            }
        }
