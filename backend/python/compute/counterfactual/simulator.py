"""
Counterfactual Simulator module for PERSEPHONE Counterfactual Research Platform.
Executes multi-patient, multi-arm RK4 mechanistic trajectory simulations across synthetic cohorts.
"""
import math
from backend.python.compute.counterfactual.treatment_matrix import TreatmentMatrix
from backend.python.compute.simulation.solvers.rk4 import rk4_step

class CounterfactualSimulator:
    """
    Simulates high-throughput virtual patient cohorts across alternative treatment arms.
    """

    @classmethod
    def simulate_scenario(cls, scenario):
        """
        Executes simulations for all cohort members across all defined treatment arms in scenario.
        Returns a structured dictionary of raw simulated results keyed by arm.
        """
        cohort = scenario.target_cohort
        duration = scenario.duration
        h = scenario.step_size_h
        steps = int(duration / h)

        raw_arm_results = {arm_id: [] for arm_id in scenario.arms}

        for arm_id in scenario.arms:
            regimen = TreatmentMatrix.get_regimen(arm_id)
            arm_simulations = []

            for member in cohort.members:
                sim_res = cls._simulate_single_twin(member, regimen, duration, h, steps)
                arm_simulations.append(sim_res)

            raw_arm_results[arm_id] = arm_simulations

        return {
            "scenario_id": scenario.scenario_id,
            "cohort_id": cohort.cohort_id,
            "cohort_size": cohort.size,
            "duration_days": duration,
            "arms_evaluated": scenario.arms,
            "arm_results": raw_arm_results
        }

    @classmethod
    def _simulate_single_twin(cls, member, regimen, duration, h, steps):
        p = member.biophysical_params

        v0 = p.get("V0", 80.0)
        fr = p.get("resistant_ratio", 0.05)
        sr0 = round(v0 * fr, 3)
        ss0 = round(v0 - sr0, 3)

        alpha1 = p.get("alpha1", 0.08)
        alpha2 = p.get("alpha2", 0.045)
        k_val = p.get("K", 200.0)
        es = p.get("ES", 0.16) * regimen.get("es_multiplier", 1.0)
        er = p.get("ER", 0.015) * regimen.get("er_multiplier", 1.0)
        ke = p.get("ke", 0.15)
        beta = p.get("beta", 0.25) * regimen.get("toxicity_multiplier", 1.0)
        gamma = p.get("gamma", 0.10)

        base_dose = regimen.get("base_dose", 10.0)
        interval = regimen.get("dosing_interval", 7)
        sched_type = regimen.get("schedule_type", "continuous_pulse")
        holiday_thresh = regimen.get("holiday_threshold")
        restart_thresh = regimen.get("restart_threshold")

        y = [ss0, sr0, 0.0, 0.0]
        cumulative_dose = 0.0
        cumulative_tox = 0.0
        peak_tox = 0.0
        nadir_vol = v0
        nadir_day = 0.0
        time_to_progression = float(duration)
        progressed = False
        resistance_day = None
        vacation_active = False

        checkpoint_days = {0, 14, 28, 56, 90, 120, 180, 240, 300, 360}
        timeline = []

        def derivatives(t_val, state, dose_val):
            ss = max(0.0, state[0])
            sr = max(0.0, state[1])
            d_conc = max(0.0, state[2])
            tox = max(0.0, state[3])
            total = ss + sr

            d_ss = alpha1 * ss * (1.0 - total / k_val) - d_conc * es * ss
            d_sr = alpha2 * sr * (1.0 - total / k_val) - d_conc * er * sr
            d_drug = dose_val - ke * d_conc
            d_tox = beta * d_conc - gamma * tox
            return [d_ss, d_sr, d_drug, d_tox]

        for step in range(steps + 1):
            t = step * h
            ss = max(0.0, y[0])
            sr = max(0.0, y[1])
            tot_vol = ss + sr
            tox = max(0.0, y[3])

            cumulative_tox += tox * h
            if tox > peak_tox:
                peak_tox = tox

            # Track nadir
            if tot_vol < nadir_vol:
                nadir_vol = tot_vol
                nadir_day = t

            # Track resistance emergence (resistant outnumbering sensitive)
            if sr > ss and resistance_day is None and t > 0:
                resistance_day = t

            # Track Progression (RECIST 20% increase over nadir or baseline)
            prog_threshold = max(v0 * 1.20, nadir_vol * 1.20)
            if tot_vol >= prog_threshold and not progressed and t >= 14:
                progressed = True
                time_to_progression = t

            # Determine dose
            current_dose = 0.0
            is_dose_time = (int(t) % interval == 0) and (abs(t - int(t)) < 1e-5)

            if sched_type == "daily_continuous":
                if abs(t - int(t)) < 1e-5:
                    current_dose = base_dose
            elif sched_type == "adaptive_vacation":
                # Adaptive vacation rules
                if tot_vol <= (holiday_thresh * v0):
                    vacation_active = True
                elif tot_vol >= (restart_thresh * v0):
                    vacation_active = False

                if is_dose_time and not vacation_active:
                    current_dose = base_dose
            else: # continuous pulse
                if is_dose_time:
                    current_dose = base_dose

            if current_dose > 0:
                cumulative_dose += current_dose

            # Sample timeline checkpoints
            int_t = int(round(t))
            if abs(t - int_t) < 1e-5 and int_t in checkpoint_days:
                timeline.append({
                    "day": int_t,
                    "total_volume": round(tot_vol, 2),
                    "sensitive_cells": round(ss, 2),
                    "resistant_cells": round(sr, 2),
                    "toxicity": round(tox, 3),
                    "dose": current_dose
                })

            # RK4 Integration step
            y = rk4_step(lambda t_curr, s_curr: derivatives(t_curr, s_curr, current_dose), t, y, h)

        depth = round(((nadir_vol - v0) / v0) * 100.0, 2)
        depth = min(0.0, depth)

        return {
            "member_id": member.member_id,
            "ttp": round(time_to_progression, 1),
            "progressed": progressed,
            "nadir_volume": round(nadir_vol, 2),
            "nadir_day": round(nadir_day, 1),
            "depth_of_response": depth,
            "cumulative_dose": round(cumulative_dose, 1),
            "cumulative_toxicity": round(cumulative_tox, 2),
            "peak_toxicity": round(peak_tox, 2),
            "resistance_emergence_day": round(resistance_day, 1) if resistance_day else None,
            "timeline": timeline
        }
