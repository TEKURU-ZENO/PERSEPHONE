"""
Counterfactual Outcomes module for PERSEPHONE Counterfactual Research Platform.
Computes Kaplan-Meier survival curves, response rates (ORR, DCR), and population metrics across arms.
"""
import statistics
import math

class CounterfactualOutcomes:
    """
    Computes population-level oncology endpoints from raw counterfactual simulation results.
    """

    @classmethod
    def compute_arm_outcomes(cls, arm_id, sim_records, duration=180):
        """
        Computes structured endpoints for a single treatment arm across a cohort.
        """
        n = len(sim_records)
        if n == 0:
            return {}

        ttps = [r["ttp"] for r in sim_records]
        depths = [r["depth_of_response"] for r in sim_records]
        doses = [r["cumulative_dose"] for r in sim_records]
        toxs = [r["cumulative_toxicity"] for r in sim_records]
        res_days = [r["resistance_emergence_day"] for r in sim_records if r["resistance_emergence_day"] is not None]

        # 1. Kaplan-Meier Survival Curve
        km_curve, median_pfs = cls._compute_kaplan_meier(sim_records, duration)

        # 2. Response Rates (RECIST criteria)
        # CR: depth <= -90%, PR: -90% < depth <= -30%, SD: -30% < depth <= 0%, PD: depth > 0%
        cr_count = sum(1 for d in depths if d <= -90.0)
        pr_count = sum(1 for d in depths if -90.0 < d <= -30.0)
        sd_count = sum(1 for d in depths if -30.0 < d <= 0.0)
        pd_count = n - (cr_count + pr_count + sd_count)

        orr = round((cr_count + pr_count) / n, 3)
        dcr = round((cr_count + pr_count + sd_count) / n, 3)

        # 3. Aggregate Metrics
        mean_ttp = round(statistics.mean(ttps), 1)
        med_ttp = round(statistics.median(ttps), 1)
        mean_dose = round(statistics.mean(doses), 1)
        mean_tox = round(statistics.mean(toxs), 2)
        med_res_day = round(statistics.median(res_days), 1) if res_days else None

        return {
            "arm_id": arm_id,
            "cohort_size": n,
            "median_pfs_days": median_pfs,
            "mean_ttp_days": mean_ttp,
            "median_ttp_days": med_ttp,
            "objective_response_rate": orr,
            "disease_control_rate": dcr,
            "response_breakdown": {
                "complete_response": cr_count,
                "partial_response": pr_count,
                "stable_disease": sd_count,
                "progressive_disease": pd_count
            },
            "mean_cumulative_dose": mean_dose,
            "mean_cumulative_toxicity": mean_tox,
            "median_resistance_emergence_day": med_res_day,
            "kaplan_meier_curve": km_curve,
            "raw_ttps": ttps,
            "raw_doses": doses,
            "raw_toxicities": toxs
        }

    @classmethod
    def _compute_kaplan_meier(cls, sim_records, duration=180):
        """
        Calculates non-parametric Kaplan-Meier survival estimator S(t) = Product(1 - d_i / n_i).
        """
        n = len(sim_records)
        # Event table: (time, is_event)
        events = sorted([(r["ttp"], 1 if r["progressed"] else 0) for r in sim_records], key=lambda x: x[0])

        current_n = n
        surv_prob = 1.0
        time_points = {}

        for t_val, is_event in events:
            if t_val not in time_points:
                time_points[t_val] = {"d": 0, "c": 0}
            if is_event:
                time_points[t_val]["d"] += 1
            else:
                time_points[t_val]["c"] += 1

        km_steps = [{"day": 0, "survival_probability": 1.0}]
        median_pfs = float(duration)
        median_found = False

        sorted_times = sorted(time_points.keys())
        at_risk = n

        for t_val in sorted_times:
            d_i = time_points[t_val]["d"]
            c_i = time_points[t_val]["c"]
            if at_risk > 0 and d_i > 0:
                surv_prob *= (1.0 - (d_i / at_risk))
            surv_prob = round(max(0.0, min(1.0, surv_prob)), 4)
            at_risk -= (d_i + c_i)

            km_steps.append({"day": round(t_val, 1), "survival_probability": surv_prob})
            if surv_prob <= 0.50 and not median_found:
                median_pfs = round(t_val, 1)
                median_found = True

        # Interpolate standard evaluation points: [0, 30, 60, 90, 120, 150, 180]
        standard_days = [0, 30, 60, 90, 120, 150, 180]
        standardized_curve = []
        for s_day in standard_days:
            # Last known survival probability at or before s_day
            p = 1.0
            for step in km_steps:
                if step["day"] <= s_day:
                    p = step["survival_probability"]
                else:
                    break
            standardized_curve.append({"day": s_day, "survival_probability": p})

        return standardized_curve, median_pfs
