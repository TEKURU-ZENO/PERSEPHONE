"""
PERSEPHONE Mechanistic LSODA IVP ODE Solver
Implements rigorous continuous-time Lotka-Volterra cross-competition simulations
with instantaneous concentration jumps at dose events and RECIST 1.1 / PCWG3 progression tracking.
Powered by scipy.integrate.solve_ivp with method='LSODA'.
"""
import numpy as np
from scipy.integrate import solve_ivp
from backend.python.compute.simulation.params import get_default_model_params
from backend.python.compute.simulation.rules.progression import (
    check_recist_progression,
    check_pcwg3_progression,
    check_simplified_progression
)

def _lotka_volterra_rhs(t, y, alpha1, alpha2, K, ES, ER, ke, beta, gamma, aSR, aRS):
    """
    RHS derivative vector: y = [S, R, C, T]
    Enforces non-negative physical states.
    """
    S = max(0.0, float(y[0]))
    R = max(0.0, float(y[1]))
    C = max(0.0, float(y[2]))
    T = max(0.0, float(y[3]))

    # Lotka-Volterra with cross-competition
    dSS = alpha1 * S * (1.0 - (S + aSR * R) / K) - ES * C * S
    dSR = alpha2 * R * (1.0 - (R + aRS * S) / K) - ER * C * R

    # PK clearing
    dC = -ke * C

    # PD Toxicity
    dT = beta * C - gamma * T

    return [dSS, dSR, dC, dT]

def simulate_lotka_volterra_lsoda(
    patient=None,
    strategy="adaptive",
    control_params=None,
    max_step=0.5,
    progression_rule="recist"
):
    """
    Simulates high-precision Lotka-Volterra dynamics using solve_ivp(method='LSODA').
    Splits integration intervals at dosing / adaptive decision events to implement
    true instantaneous concentration jumps C <- C + D.
    """
    defaults = get_default_model_params()
    control_params = control_params or {}

    p_params = {}
    if patient:
        p_params = getattr(patient, "model_params", {}) or {}
        if not isinstance(p_params, dict):
            p_params = {}

    # Extract ODE parameters
    a1 = float(control_params.get("alpha1", p_params.get("alpha1", defaults["alpha1"])))
    a2 = float(control_params.get("alpha2", p_params.get("alpha2", defaults["alpha2"])))
    K_val = float(control_params.get("K", p_params.get("K", defaults["K"])))
    es = float(control_params.get("ES", p_params.get("ES", defaults["ES"])))
    er = float(control_params.get("ER", p_params.get("ER", defaults["ER"])))
    ke = float(control_params.get("ke", p_params.get("ke", defaults["ke"])))
    beta = float(control_params.get("beta", p_params.get("beta", defaults["beta"])))
    gamma = float(control_params.get("gamma", p_params.get("gamma", defaults["gamma"])))
    aSR = float(control_params.get("aSR", p_params.get("aSR", defaults.get("aSR", 1.0))))
    aRS = float(control_params.get("aRS", p_params.get("aRS", defaults.get("aRS", 1.0))))

    # Initial states
    SS_init = float(control_params.get("SS_init", p_params.get("SS_init", 80.0)))
    SR_init = float(control_params.get("SR_init", p_params.get("SR_init", 2.0)))
    if control_params.get("initialResistantRatio") is not None:
        total_vol = SS_init + SR_init
        SR_init = total_vol * (float(control_params["initialResistantRatio"]) / 100.0)
        SS_init = total_vol - SR_init

    V0 = SS_init + SR_init
    y_current = np.array([SS_init, SR_init, 0.0, 0.0], dtype=float)

    duration = float(control_params.get("duration", 180.0))
    mtd_dose = float(control_params.get("mtdDose", 10.0))
    interval = float(control_params.get("dosingInterval", 7.0))
    sampling_dt = float(control_params.get("sampling_dt", 0.5))

    # Event schedule
    event_times = np.arange(0.0, duration + interval, interval)
    event_times = [t for t in event_times if t <= duration]
    if duration not in event_times:
        event_times.append(duration)

    timeline = []
    active_therapy = True
    cumulative_dose = 0.0
    time_to_progression = duration
    nadir_volume = V0
    current_time = 0.0

    timeline.append({
        "day": 0.0,
        "sensitive": float(y_current[0]),
        "resistant": float(y_current[1]),
        "totalVolume": float(y_current[0] + y_current[1]),
        "drugConcentration": float(y_current[2]),
        "toxicity": float(y_current[3]),
        "dose": 0.0
    })

    for i in range(len(event_times) - 1):
        t_start = event_times[i]
        t_end = event_times[i + 1]

        total_vol_now = float(y_current[0] + y_current[1])
        if total_vol_now < nadir_volume:
            nadir_volume = total_vol_now

        # Determine dose applied at t_start
        dose_applied = 0.0
        strat_lower = strategy.lower()

        if strat_lower == "mtd":
            dose_applied = mtd_dose
        elif strat_lower == "adaptive":
            if active_therapy and total_vol_now < 0.5 * V0:
                active_therapy = False
            elif not active_therapy and total_vol_now > 1.0 * V0:
                active_therapy = True

            dose_applied = mtd_dose if active_therapy else 0.0
        elif strat_lower == "control":
            dose_applied = 0.0

        # Apply instantaneous concentration jump: C <- C + D
        y_current[2] += dose_applied
        cumulative_dose += dose_applied

        # Continuous LSODA integration over interval [t_start, t_end]
        t_eval = np.arange(t_start + sampling_dt, t_end + 1e-9, sampling_dt)
        if len(t_eval) == 0:
            t_eval = np.array([t_end])

        sol = solve_ivp(
            fun=_lotka_volterra_rhs,
            t_span=(t_start, t_end),
            y0=y_current,
            args=(a1, a2, K_val, es, er, ke, beta, gamma, aSR, aRS),
            method="LSODA",
            t_eval=t_eval,
            max_step=max_step,
            rtol=1e-6,
            atol=1e-8
        )

        for s_idx in range(len(sol.t)):
            step_t = float(sol.t[s_idx])
            step_s = max(0.0, float(sol.y[0][s_idx]))
            step_r = max(0.0, float(sol.y[1][s_idx]))
            step_c = max(0.0, float(sol.y[2][s_idx]))
            step_tox = max(0.0, float(sol.y[3][s_idx]))
            step_vol = step_s + step_r

            if step_vol < nadir_volume:
                nadir_volume = step_vol

            # Check progression
            is_pd = False
            if progression_rule == "recist":
                is_pd = check_recist_progression(step_vol, nadir_volume)
            elif progression_rule == "pcwg3":
                is_pd = check_pcwg3_progression(step_vol, nadir_volume)
            else:
                is_pd = check_simplified_progression(step_vol, V0)

            if is_pd and time_to_progression == duration and step_t > 5.0:
                time_to_progression = step_t

            timeline.append({
                "day": step_t,
                "sensitive": step_s,
                "resistant": step_r,
                "totalVolume": step_vol,
                "drugConcentration": step_c,
                "toxicity": step_tox,
                "dose": dose_applied if s_idx == 0 else 0.0
            })

        y_current = np.array([
            max(0.0, float(sol.y[0][-1])),
            max(0.0, float(sol.y[1][-1])),
            max(0.0, float(sol.y[2][-1])),
            max(0.0, float(sol.y[3][-1]))
        ])

    max_tox = max(pt["toxicity"] for pt in timeline) if timeline else 0.0

    return {
        "timeline": timeline,
        "timeToProgression": time_to_progression,
        "cumulativeDose": round(cumulative_dose, 2),
        "maxToxicity": round(max_tox, 3),
        "baselineVolume": V0,
        "nadirVolume": round(nadir_volume, 3),
        "progressionRule": progression_rule
    }
