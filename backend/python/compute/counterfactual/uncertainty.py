"""
Counterfactual Uncertainty Engine module for PERSEPHONE Counterfactual Research Platform.
Provides rigorous uncertainty quantification (95% CIs) across all comparative outcomes:
ATE, Delta Toxicity, Dose Reduction Ratio, Therapeutic Efficiency Index (TEI), and Resistance Emergence.
"""
import math
import statistics

class CounterfactualUncertaintyEngine:
    """
    Computes confidence intervals and uncertainty distributions across counterfactual comparative metrics.
    """

    @classmethod
    def estimate_comparison_uncertainty(cls, control_records, arm_records, ci_level=0.95):
        """
        Calculates 95% confidence intervals for all comparative treatment effects.
        """
        z_crit = 1.96 if ci_level == 0.95 else 2.576 # 99%
        n = min(len(control_records), len(arm_records))
        if n < 2:
            return {}

        ctrl_ttps = [r["ttp"] for r in control_records[:n]]
        arm_ttps = [r["ttp"] for r in arm_records[:n]]

        ctrl_toxs = [r["cumulative_toxicity"] for r in control_records[:n]]
        arm_toxs = [r["cumulative_toxicity"] for r in arm_records[:n]]

        ctrl_doses = [r["cumulative_dose"] for r in control_records[:n]]
        arm_doses = [r["cumulative_dose"] for r in arm_records[:n]]

        # Paired differences across the synthetic digital twins
        diff_ttps = [arm_ttps[i] - ctrl_ttps[i] for i in range(n)]
        diff_toxs = [arm_toxs[i] - ctrl_toxs[i] for i in range(n)]
        diff_doses = [ctrl_doses[i] - arm_doses[i] for i in range(n)]

        # 1. ATE (Average Treatment Effect on TTP in days) ± CI
        mean_ate = statistics.mean(diff_ttps)
        se_ate = (statistics.stdev(diff_ttps) / math.sqrt(n)) if n > 1 else 0.0
        ate_lower = mean_ate - z_crit * se_ate
        ate_upper = mean_ate + z_crit * se_ate

        # 2. Delta Toxicity ± CI
        mean_delta_tox = statistics.mean(diff_toxs)
        se_tox = (statistics.stdev(diff_toxs) / math.sqrt(n)) if n > 1 else 0.0
        tox_lower = mean_delta_tox - z_crit * se_tox
        tox_upper = mean_delta_tox + z_crit * se_tox

        # 3. Dose Reduction Ratio (%) ± CI
        mean_ctrl_dose = statistics.mean(ctrl_doses)
        mean_arm_dose = statistics.mean(arm_doses)
        mean_dose_red = ((mean_ctrl_dose - mean_arm_dose) / max(mean_ctrl_dose, 1.0)) * 100.0
        # Delta method for percentage reduction
        dose_red_pcts = [((ctrl_doses[i] - arm_doses[i]) / max(ctrl_doses[i], 1.0)) * 100.0 for i in range(n)]
        se_dose_red = (statistics.stdev(dose_red_pcts) / math.sqrt(n)) if n > 1 else 0.0
        dose_red_lower = mean_dose_red - z_crit * se_dose_red
        dose_red_upper = mean_dose_red + z_crit * se_dose_red

        # 4. Therapeutic Efficiency Index (TEI = ATE / Cumulative Dose) ± CI
        tei_val = mean_ate / max(mean_arm_dose, 1.0)
        tei_samples = [diff_ttps[i] / max(arm_doses[i], 1.0) for i in range(n)]
        se_tei = (statistics.stdev(tei_samples) / math.sqrt(n)) if n > 1 else 0.0
        tei_lower = tei_val - z_crit * se_tei
        tei_upper = tei_val + z_crit * se_tei

        # 5. Resistance Emergence Horizon Delta ± CI
        ctrl_res = [r["resistance_emergence_day"] for r in control_records[:n] if r["resistance_emergence_day"] is not None]
        arm_res = [r["resistance_emergence_day"] for r in arm_records[:n] if r["resistance_emergence_day"] is not None]

        if ctrl_res and arm_res:
            m_res = min(len(ctrl_res), len(arm_res))
            diff_res = [arm_res[i] - ctrl_res[i] for i in range(m_res)]
            mean_res_delta = statistics.mean(diff_res)
            se_res = (statistics.stdev(diff_res) / math.sqrt(m_res)) if m_res > 1 else 0.0
            res_lower = mean_res_delta - z_crit * se_res
            res_upper = mean_res_delta + z_crit * se_res
        else:
            mean_res_delta = 0.0
            res_lower = 0.0
            res_upper = 0.0

        return {
            "ate_ttp_days": cls._pack_uncertainty(mean_ate, ate_lower, ate_upper, 1, ci_level),
            "delta_toxicity": cls._pack_uncertainty(mean_delta_tox, tox_lower, tox_upper, 2, ci_level),
            "dose_reduction_percent": cls._pack_uncertainty(mean_dose_red, dose_red_lower, dose_red_upper, 1, ci_level),
            "therapeutic_efficiency_index": cls._pack_uncertainty(tei_val, tei_lower, tei_upper, 4, ci_level),
            "resistance_emergence_delta_days": cls._pack_uncertainty(mean_res_delta, res_lower, res_upper, 1, ci_level)
        }

    @staticmethod
    def _pack_uncertainty(value, lower, upper, decimals=2, ci_level=0.95):
        return {
            "value": round(float(value), decimals),
            "uncertainty": {
                "lower_bound": round(float(lower), decimals),
                "upper_bound": round(float(upper), decimals),
                "ci_level": ci_level
            }
        }
