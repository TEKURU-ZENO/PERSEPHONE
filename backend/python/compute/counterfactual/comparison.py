"""
Counterfactual Comparator module for PERSEPHONE Counterfactual Research Platform.
Computes head-to-head statistical superiority, Hazard Ratios, Log-rank p-values,
Delta TTP uncertainty, and ranks arms based on best-performing simulated strategy.
"""
import math
from backend.python.compute.counterfactual.uncertainty import CounterfactualUncertaintyEngine
from backend.python.compute.counterfactual.provenance import ScenarioProvenanceEngine
from backend.python.compute.counterfactual.treatment_matrix import TreatmentMatrix

class CounterfactualComparator:
    """
    Compares multi-arm counterfactual regimens against control with comprehensive uncertainty.
    """

    @classmethod
    def compare_arms(cls, simulation_output, outcomes_by_arm, control_arm="mtd", anchor_patient_id="patient-a"):
        """
        Executes head-to-head statistical comparison of all arms against control_arm.
        """
        raw_results = simulation_output.get("arm_results", {})
        if control_arm not in raw_results:
            control_arm = list(raw_results.keys())[0] if raw_results else "mtd"

        control_sims = raw_results.get(control_arm, [])
        control_outcomes = outcomes_by_arm.get(control_arm, {})
        ctrl_med_pfs = max(1.0, control_outcomes.get("median_pfs_days", 90.0))

        comparisons = {}
        arm_scores = []

        for arm_id, arm_sims in raw_results.items():
            if arm_id == control_arm:
                continue

            arm_outcomes = outcomes_by_arm.get(arm_id, {})
            arm_med_pfs = max(1.0, arm_outcomes.get("median_pfs_days", 90.0))

            # Check for observed progression events
            ctrl_events = sum(1 for r in control_sims if r.get("progressed"))
            arm_events = sum(1 for r in arm_sims if r.get("progressed"))
            total_events = ctrl_events + arm_events

            if total_events == 0:
                # 0 events observed: Cox HR and log-rank test are mathematically undefined / non-estimable
                hr_block = {
                    "value": None,
                    "interpretation": "not estimable (0 progression events)",
                    "uncertainty": {
                        "lower_bound": None,
                        "upper_bound": None,
                        "ci_level": 0.95,
                        "status": "not estimable (0 progression events)"
                    },
                    "status": "not estimable (0 progression events)"
                }
                log_rank_block = {
                    "chi_square": 0.0,
                    "p_value": None,
                    "statistically_significant": False,
                    "status": "not estimable (0 progression events)"
                }
            else:
                # 1. Hazard Ratio (Cox proportional hazards approximation)
                # HR < 1.0 indicates reduced hazard of progression (superior survival)
                hr_approx = round(ctrl_med_pfs / arm_med_pfs, 3)
                # Uncertainty for HR
                n_eff = max(4, min(len(control_sims), len(arm_sims)))
                se_ln_hr = math.sqrt(4.0 / n_eff)
                hr_lower = round(math.exp(math.log(hr_approx) - 1.96 * se_ln_hr), 3)
                hr_upper = round(math.exp(math.log(hr_approx) + 1.96 * se_ln_hr), 3)

                # 2. Log-rank test statistic approximation
                diff_med = arm_med_pfs - ctrl_med_pfs
                chi2_stat = round((diff_med ** 2) / max(10.0, (ctrl_med_pfs + arm_med_pfs) / 2.0), 2)
                # Simple 1-df p-value approximation
                p_val = round(max(0.0001, math.exp(-0.5 * chi2_stat)), 4) if chi2_stat > 0 else 1.0

                hr_block = {
                    "value": hr_approx,
                    "interpretation": "Superior" if hr_approx < 0.85 else ("Inferior" if hr_approx > 1.15 else "Equivalent"),
                    "uncertainty": {
                        "lower_bound": hr_lower,
                        "upper_bound": hr_upper,
                        "ci_level": 0.95
                    }
                }
                log_rank_block = {
                    "chi_square": chi2_stat,
                    "p_value": p_val,
                    "statistically_significant": bool(p_val < 0.05)
                }

            # 3. Uncertainty across Delta TTP, Delta Tox, Dose Reduction, TEI, Resistance Emergence
            uncertainty_block = CounterfactualUncertaintyEngine.estimate_comparison_uncertainty(
                control_sims, arm_sims, ci_level=0.95
            )

            # 4. Multi-objective simulated utility score
            # Balancing efficacy (TTP gain), toxicity reduction, and dose savings
            ate_val = uncertainty_block.get("ate_ttp_days", {}).get("value", 0.0)
            dose_red = uncertainty_block.get("dose_reduction_percent", {}).get("value", 0.0)
            delta_tox = uncertainty_block.get("delta_toxicity", {}).get("value", 0.0)

            # Higher utility = longer TTP, lower dose, lower toxicity
            utility = (
                (ate_val / 60.0) * 0.45 +
                (dose_red / 100.0) * 0.30 -
                (delta_tox / 20.0) * 0.25
            )
            utility_score = round(utility, 3)

            comparisons[arm_id] = {
                "intervention_arm": arm_id,
                "control_arm": control_arm,
                "hazard_ratio": hr_block,
                "log_rank_test": log_rank_block,
                "delta_ttp": uncertainty_block.get("ate_ttp_days"),
                "delta_toxicity": uncertainty_block.get("delta_toxicity"),
                "dose_reduction_percent": uncertainty_block.get("dose_reduction_percent"),
                "therapeutic_efficiency_index": uncertainty_block.get("therapeutic_efficiency_index"),
                "resistance_emergence_delta_days": uncertainty_block.get("resistance_emergence_delta_days"),
                "simulated_utility_score": utility_score,
                "scenario_manifest": ScenarioProvenanceEngine.generate_scenario_manifest(control_arm, arm_id, "delta_TTP")
            }

            arm_scores.append((arm_id, utility_score))

        # Rank alternative arms by simulated utility
        arm_scores.sort(key=lambda x: x[1], reverse=True)
        best_arm = arm_scores[0][0] if arm_scores else control_arm

        regimen_info = TreatmentMatrix.get_regimen(best_arm)

        return {
            "control_arm": control_arm,
            "comparisons": comparisons,
            "ranked_arms": [a[0] for a in arm_scores],
            "best_performing_simulated_strategy": {
                "arm_id": best_arm,
                "name": regimen_info.get("name"),
                "category": regimen_info.get("category"),
                "utility_score": arm_scores[0][1] if arm_scores else 0.0,
                "rationale": (
                    f"Arm '{best_arm}' achieved highest multi-objective utility under mechanistic simulation assumptions: "
                    f"Delta TTP = +{(comparisons.get(best_arm, {}).get('delta_ttp') or {}).get('value', 0)} days, "
                    f"Dose Reduction = {(comparisons.get(best_arm, {}).get('dose_reduction_percent') or {}).get('value', 0)}%."
                ),
                "qualification": "Best-performing under simulated biophysical Lotka-Volterra assumptions; not a clinical recommendation.",
                "model_version": "counterfactual-v1",
                "calibration_status": "research"
            },
            "disclaimer": "FOR RESEARCH USE ONLY: Simulated research projection under synthetic cohort assumptions; not a clinical directive."
        }
