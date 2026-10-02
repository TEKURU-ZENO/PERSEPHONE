"""
Multimodal Consistency Module for PERSEPHONE Governance Platform.
Quantifies concordance across disparate diagnostic modalities:
Genomic biomarkers vs Imaging volumetric response vs Longitudinal tumor velocity.
"""
from typing import Dict, List, Any, Optional


class ConsistencyAuditor:
    """
    Evaluates cross-modal agreement and detects paradoxical clinical divergence.
    """

    @classmethod
    def evaluate_multimodal_consistency(
        cls,
        patient_data: Dict[str, Any],
        imaging_signals: Optional[Dict[str, Any]] = None,
        monitoring_signals: Optional[Dict[str, Any]] = None,
        proposed_drug: str = "Olaparib"
    ) -> Dict[str, Any]:
        imaging_signals = imaging_signals or {}
        monitoring_signals = monitoring_signals or {}

        # 1. Genomic signal
        variants = [str(v).upper() for v in (patient_data.get("variants") or [])]
        hrd_score = float(patient_data.get("hrd_score", 55.0 if any("BRCA" in v for v in variants) else 20.0))
        genomic_sensitivity = "SENSITIVE" if (any("BRCA" in v for v in variants) or hrd_score >= 42.0) else "RESISTANT"

        # 2. Imaging signal
        recist_status = str(imaging_signals.get("recist_status", imaging_signals.get("response", "PR"))).upper()
        volume_delta_pct = float(imaging_signals.get("volume_delta_pct", imaging_signals.get("delta_volume", -25.0)))
        necrotic_fraction = float(imaging_signals.get("necrotic_fraction", 0.15))

        imaging_assessment = "RESPONSIVE" if (volume_delta_pct < 0 or recist_status in ["CR", "PR"]) else "PROGRESSIVE"

        # 3. Longitudinal trajectory velocity
        current_velocity = float(monitoring_signals.get("current_velocity", monitoring_signals.get("velocity", 0.0)))
        velocity_trend = "GROWING" if current_velocity > 0.1 else ("SHRINKING" if current_velocity < -0.1 else "STABLE")

        # 4. Discordance Detection
        discordance_flags = []
        discordance_score = 0.0

        # Paradox 1: Genomic Sensitive BUT Imaging Progressive
        if genomic_sensitivity == "SENSITIVE" and (imaging_assessment == "PROGRESSIVE" or volume_delta_pct > 15.0 or current_velocity > 0.5):
            discordance_flags.append({
                "type": "GENOMIC_IMAGING_PARADOX",
                "severity": "CRITICAL",
                "statement": f"Genomic markers predict sensitivity to {proposed_drug} (BRCAm/HRD+), but longitudinal imaging and trajectory demonstrate rapid progression ({volume_delta_pct:+.1f}%, velocity {current_velocity:+.2f} cm3/day).",
                "implication": "Possible emergent secondary resistance (reversion mutation) or false genomic signal."
            })
            discordance_score += 0.65

        # Paradox 2: Genomic Resistant BUT Imaging Rapidly Responding
        elif genomic_sensitivity == "RESISTANT" and (imaging_assessment == "RESPONSIVE" and volume_delta_pct < -30.0):
            discordance_flags.append({
                "type": "UNEXPECTED_EXCEPTIONAL_RESPONSE",
                "severity": "MODERATE",
                "statement": f"Tumor shows dramatic shrinkage ({volume_delta_pct:.1f}%) despite genomic profile lacking canonical sensitivity biomarkers.",
                "implication": "Off-target biological sensitivity or uncharacterized synthetic lethality pathway."
            })
            discordance_score += 0.35

        # Paradox 3: Expanding necrotic core under static volume
        if abs(volume_delta_pct) < 10.0 and necrotic_fraction > 0.50:
            discordance_flags.append({
                "type": "PSEUDOPROGRESSION_OR_CENTRAL_NECROSIS",
                "severity": "MODERATE",
                "statement": f"Tumor dimensions are stable but necrotic core has expanded to {necrotic_fraction*100:.0f}%, indicating non-volumetric cytocidal treatment effect.",
                "implication": "Volumetric RECIST may underestimate true clinical response; Choi criteria recommended."
            })
            discordance_score += 0.25

        discordance_index = round(min(1.0, discordance_score), 2)
        concordant = len(discordance_flags) == 0 or discordance_index < 0.40

        return {
            "is_concordant": concordant,
            "discordance_index": discordance_index,
            "signals": {
                "genomic_sensitivity": genomic_sensitivity,
                "imaging_assessment": imaging_assessment,
                "velocity_trend": velocity_trend,
                "volume_delta_pct": volume_delta_pct,
                "current_velocity_cm3_per_day": current_velocity,
                "necrotic_fraction": necrotic_fraction
            },
            "discordance_flags_count": len(discordance_flags),
            "discordance_flags": discordance_flags,
            "recommendation": "PROCEED" if concordant else "TRIGGER_CLINICAL_ABSTENTION_AND_REBIOPSY"
        }
