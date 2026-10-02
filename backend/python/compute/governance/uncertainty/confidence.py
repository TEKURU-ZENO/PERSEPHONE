"""
Uncertainty Confidence Decomposition Module for PERSEPHONE Governance Platform.
Decomposes total predictive uncertainty into Epistemic (knowledge deficit / sparse data)
and Aleatoric (intrinsic biological stochasticity) components.
"""
from typing import Dict, List, Any, Optional


class UncertaintyDecomposer:
    """
    Quantifies and decomposes uncertainty across clinical modalities.
    """

    @classmethod
    def decompose_uncertainty(
        cls,
        evidence_count: int,
        multimodal_discordance: float,
        drift_psi: float,
        base_model_confidence: float = 0.85
    ) -> Dict[str, Any]:
        """
        Decomposes total uncertainty:
        Epistemic Uncertainty: Driven by low evidence count, high drift PSI, and sparse literature.
        Aleatoric Uncertainty: Driven by biological tumor heterogeneity and subclonal plasticity.
        """
        # Epistemic: Higher if evidence is low or feature distribution is drifted
        evidence_penalty = max(0.0, 1.0 - (evidence_count / 4.0)) * 0.45
        drift_penalty = min(0.40, drift_psi * 0.8)
        epistemic_uncertainty = round(min(1.0, evidence_penalty + drift_penalty), 3)

        # Aleatoric: Higher if cross-modal discordance is observed
        aleatoric_uncertainty = round(min(1.0, multimodal_discordance * 0.70 + 0.15), 3)

        # Total uncertainty combines both
        total_uncertainty = round(min(1.0, (epistemic_uncertainty * 0.6) + (aleatoric_uncertainty * 0.4)), 3)

        # Calibrated synthesized confidence
        calibrated_confidence = round(max(0.05, min(0.99, base_model_confidence * (1.0 - total_uncertainty * 0.65))), 3)

        return {
            "calibrated_confidence": calibrated_confidence,
            "total_uncertainty": total_uncertainty,
            "epistemic_uncertainty": epistemic_uncertainty,
            "aleatoric_uncertainty": aleatoric_uncertainty,
            "factors": {
                "evidence_support_factor": round(1.0 - evidence_penalty, 3),
                "drift_stability_factor": round(1.0 - drift_penalty, 3),
                "multimodal_concordance_factor": round(1.0 - multimodal_discordance, 3)
            }
        }
