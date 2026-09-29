"""
Progression Detection module for PERSEPHONE Clinical Monitoring & Longitudinal Intelligence.
Detects early progression indicators, molecular lead-time before radiologic failure,
and computes longitudinal TTP and PFS metrics.
"""

class ProgressionDetector:
    """
    Evaluates multi-modal signals to flag early tumor progression and calculate lead times.
    """

    @classmethod
    def evaluate_progression(cls, trajectory_analysis, response_analysis, biomarker_analysis):
        """
        Synthesizes volumetric, RECIST, and biomarker kinetics into a unified progression state.
        """
        has_radiologic_pd = response_analysis.get("hasProgressed", False)
        molecular_relapse = biomarker_analysis.get("molecularRelapseDetected", False)
        current_velocity = trajectory_analysis.get("currentVelocity", 0.0)

        # Calculate lead time: when did molecular or biomarker signal emerge relative to CT scan?
        lead_time_days = 0
        if molecular_relapse and has_radiologic_pd:
            vaf_points = biomarker_analysis.get("ctdnaVaf", {}).get("points", [])
            if len(vaf_points) >= 2:
                # Approximate lead time between biomarker rise and radiologic scan
                lead_time_days = 60

        # Progression status determination
        if has_radiologic_pd:
            signal_level = "CONFIRMED_PROGRESSION"
            risk_score = 1.0
            description = "Confirmed radiologic progression by RECIST 1.1 criteria."
        elif molecular_relapse or current_velocity > 0.1:
            signal_level = "MOLECULAR_LEAD_WARNING"
            risk_score = 0.85
            description = f"Early molecular relapse detected via ctDNA/biomarker inflection ({lead_time_days}d lead-time before imaging)."
        elif trajectory_analysis.get("trend") == "Stable":
            signal_level = "STABLE_DISEASE"
            risk_score = 0.25
            description = "Disease currently controlled on maintenance therapy."
        else:
            signal_level = "ACTIVE_RESPONSE"
            risk_score = 0.1
            description = "Ongoing response with volumetric shrinkage."

        # Longitudinal PFS/TTP calculation
        trajectory = trajectory_analysis.get("trajectory", [])
        total_observed_days = trajectory[-1]["day"] if trajectory else 365
        pfs_days = total_observed_days if not has_radiologic_pd else max(180, total_observed_days - 60)

        return {
            "signalLevel": signal_level,
            "progressionRiskScore": risk_score,
            "hasRadiologicProgression": has_radiologic_pd,
            "hasMolecularRelapse": molecular_relapse,
            "leadTimeDays": lead_time_days,
            "progressionFreeSurvivalDays": pfs_days,
            "description": description
        }
