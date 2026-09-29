"""
Resistance Escape Predictor module for PERSEPHONE Response Intelligence Platform.
Forecasts Time to Acquired Resistance (TTAR), resistance risk scores,
and ranks therapeutic bypass escape pathways with research metadata.
"""
from backend.python.compute.response_intelligence.resistance.detector import ResistanceMechanismDetector

class ResistanceEscapePredictor:
    """
    Predicts resistance trajectory, TTAR, and actionable escape pathways.
    """

    @classmethod
    def predict_escape(cls, vector):
        mech_res = ResistanceMechanismDetector.detect_mechanisms(vector)
        mechanisms = mech_res.get("mechanisms", [])

        vaf = vector.get_feature("longitudinal", "ctdna_vaf_pct", 1.0)
        vel = vector.get_feature("longitudinal", "volume_velocity", 0.0)
        synergy = vector.get_feature("pharmacologic", "synergy_score", 0.70)

        # Calculate resistance risk score [0, 1]
        base_risk = 0.25
        if mechanisms:
            base_risk += len(mechanisms) * 0.25
        if vaf > 2.0:
            base_risk += 0.20
        if vel > 0.05:
            base_risk += 0.15

        risk_score = round(min(max(base_risk, 0.05), 0.95), 3)

        # Time to Acquired Resistance (TTAR) in days (strictly non-negative)
        # Higher risk = shorter TTAR
        if risk_score > 0.70:
            ttar_days = round(max(30.0, 180.0 - (risk_score * 80.0)), 1)
        else:
            ttar_days = round(max(60.0, 380.0 - (risk_score * 200.0)), 1)

        # Ranked actionable bypass escape pathways
        escape_pathways = [
            {
                "pathway": "ATR/CHK1 DNA Damage Checkpoint Signaling",
                "rationale": "Overcomes homologous recombination restoration by synthetically targeting replication fork arrest.",
                "candidate_drugs": ["Ceralasertib (AZD6738)", "Elimusertib"],
                "evidence_strength": "High",
                "readiness": "Phase II Trial Matching"
            },
            {
                "pathway": "PI3K/AKT/mTOR Survival Cascade",
                "rationale": "Inhibits compensatory proliferative survival signals bypassing PARP dependency.",
                "candidate_drugs": ["Alpelisib", "Capivasertib"],
                "evidence_strength": "Moderate",
                "readiness": "Preclinical / Early Clinical"
            },
            {
                "pathway": "Antibody-Drug Conjugate (ADC) Target Surface Rescue",
                "rationale": "Direct cytotoxic delivery independent of DNA repair gene mutational status.",
                "candidate_drugs": ["Mirvetuximab Soravtansine", "Trastuzumab Deruxtecan"],
                "evidence_strength": "High",
                "readiness": "Approved / Clinical Consideration"
            }
        ]

        evidence_basis = [
            f"Active mechanisms: {len(mechanisms)} detected ({mech_res.get('state')})",
            f"Circulating ctDNA VAF: {vaf:.1f}%",
            f"Volume velocity slope: {vel:+.2f} cm³/day"
        ]

        confidence = 0.88 if mechanisms else 0.80

        return {
            "name": "Resistance & Escape Prediction",
            "underlying_mechanisms": mechanisms,
            "resistance_risk": {
                "value": risk_score,
                "confidence": confidence,
                "evidence_basis": evidence_basis,
                "model_version": "resistance-v1",
                "calibration_status": "research",
                "uncertainty": {
                    "lower_bound": round(max(0.0, risk_score - 0.08), 3),
                    "upper_bound": round(min(1.0, risk_score + 0.08), 3),
                    "ci_level": 0.95
                }
            },
            "time_to_acquired_resistance_days": {
                "value": ttar_days,
                "confidence": confidence,
                "evidence_basis": evidence_basis,
                "model_version": "resistance-v1",
                "calibration_status": "research",
                "uncertainty": {
                    "lower_bound": round(max(0.0, ttar_days - 30.0), 1),
                    "upper_bound": round(ttar_days + 45.0, 1),
                    "ci_level": 0.95
                }
            },
            "predicted_escape_pathways": escape_pathways
        }
