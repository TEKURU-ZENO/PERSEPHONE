"""
backend/python/compute/clinical_validation/calibration/fit_ias.py

Mechanistic Parameter Fitting and Structural/Practical Identifiability Analysis
for Lotka-Volterra Cross-Competition Models on Authentic Clinical IAS Data
(Bruchovsky et al., Cancer 2006; Tanaka et al., Phil. Trans. R. Soc. A 2010).

Standing Rules Enforced:
  - Loss function: Log-PSA squared error (PSA is log-normally distributed in vivo).
  - Bounds sourced from research/model_params.json.
  - Multi-start optimization with >= 20 random restarts to avoid local minima.
  - Exact Jacobian-based covariance, 95% confidence intervals, and condition number.
  - Profile likelihood evaluation for key parameters (r_S, r_R, a_RS).
  - Identification and flagging of collinear / unidentifiable parameter pairs.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import least_squares

from backend.python.compute.clinical_validation.calibration.ias_loader import (
    IASMeasurement,
    IASPatient,
    load_all_ias_patients,
    load_ias_patient_from_file,
)
from backend.python.compute.simulation.params import load_model_params

EPSILON = 1e-4


@dataclass
class ProfileLikelihoodResult:
    parameter: str
    grid_values: List[float]
    profile_losses: List[float]
    is_flat: bool
    relative_variation: float


@dataclass
class IASFitResult:
    patient_id: str
    cohort: str
    log_psa_rmse: float
    fitted_parameters: Dict[str, float]
    confidence_intervals_95: Dict[str, Tuple[float, float]]
    condition_number: float
    collinear_pairs: List[Dict[str, Any]]
    unidentifiable_parameters: List[str]
    profile_likelihoods: Dict[str, Dict[str, Any]]
    parameter_correlation_matrix: List[List[float]]
    parameter_names: List[str]
    observed_psa: List[Dict[str, Any]]
    predicted_psa: List[Dict[str, Any]]
    random_seed: int
    n_restarts: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _build_treatment_schedule(
    measurements: List[IASMeasurement],
) -> List[Tuple[float, float, int]]:
    """
    Constructs contiguous [t_start, t_end, treatment_status] intervals
    from longitudinal clinical visit records.
    """
    if not measurements:
        return []

    t0 = measurements[0].elapsed_days
    intervals: List[Tuple[float, float, int]] = []

    for i in range(len(measurements) - 1):
        t_start = measurements[i].elapsed_days - t0
        t_end = measurements[i + 1].elapsed_days - t0
        tx = measurements[i].treatment_status
        if t_end > t_start:
            intervals.append((t_start, t_end, tx))

    # Final measurement extension if needed
    if not intervals and len(measurements) == 1:
        intervals.append((0.0, 1.0, measurements[0].treatment_status))

    # Merge contiguous intervals with identical treatment status
    merged: List[Tuple[float, float, int]] = []
    for interval in intervals:
        if not merged:
            merged.append(interval)
        else:
            prev_start, prev_end, prev_tx = merged[-1]
            curr_start, curr_end, curr_tx = interval
            if curr_tx == prev_tx and abs(curr_start - prev_end) < 1e-6:
                merged[-1] = (prev_start, curr_end, prev_tx)
            else:
                merged.append(interval)

    return merged


def simulate_lotka_volterra_psa(
    t_eval: np.ndarray,
    tx_schedule: List[Tuple[float, float, int]],
    r_S: float,
    r_R: float,
    K: float,
    k_S: float,
    k_R: float,
    a_SR: float,
    a_RS: float,
    f_R: float,
    V_0: float,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Simulates Lotka-Volterra competition over a piecewise treatment schedule.
    Returns: (t_eval, sensitive_burden, resistant_burden)
    Total PSA = sensitive + resistant.
    """
    S_curr = max(0.0, (1.0 - f_R) * V_0)
    R_curr = max(0.0, f_R * V_0)

    t_out: List[float] = []
    S_out: List[float] = []
    R_out: List[float] = []

    for k, (t_start, t_end, tx) in enumerate(tx_schedule):
        is_last = (k == len(tx_schedule) - 1)
        if is_last:
            pts = t_eval[(t_eval >= t_start - 1e-9) & (t_eval <= t_end + 1e-9)]
        else:
            pts = t_eval[(t_eval >= t_start - 1e-9) & (t_eval < t_end - 1e-9)]

        def rhs(t: float, y: np.ndarray) -> List[float]:
            s = max(0.0, float(y[0]))
            r = max(0.0, float(y[1]))
            ds = r_S * s * (1.0 - (s + a_SR * r) / K) - k_S * tx * s
            dr = r_R * r * (1.0 - (r + a_RS * s) / K) - k_R * tx * r
            return [ds, dr]

        if len(pts) == 0:
            sol = solve_ivp(
                rhs,
                (t_start, t_end),
                [S_curr, R_curr],
                method="RK45",
                rtol=1e-5,
                atol=1e-7,
            )
            S_curr = max(0.0, float(sol.y[0][-1]))
            R_curr = max(0.0, float(sol.y[1][-1]))
            continue

        eval_grid = np.unique(np.concatenate([[t_start, t_end], pts]))
        sol = solve_ivp(
            rhs,
            (t_start, t_end),
            [S_curr, R_curr],
            method="RK45",
            t_eval=eval_grid,
            rtol=1e-5,
            atol=1e-7,
        )

        for p in pts:
            idx = int(np.argmin(np.abs(sol.t - p)))
            t_out.append(float(p))
            S_out.append(max(0.0, float(sol.y[0][idx])))
            R_out.append(max(0.0, float(sol.y[1][idx])))

        S_curr = max(0.0, float(sol.y[0][-1]))
        R_curr = max(0.0, float(sol.y[1][-1]))

    order = np.argsort(t_out)
    return (
        np.array(t_out)[order],
        np.array(S_out)[order],
        np.array(R_out)[order],
    )


def fit_ias_patient(
    patient: IASPatient,
    cycle_nums: Optional[List[int]] = None,
    n_restarts: int = 20,
    random_seed: int = 42,
    run_profile_likelihood: bool = True,
) -> IASFitResult:
    """
    Fits Lotka-Volterra mechanistic parameters to an IAS patient trajectory
    using multi-start bounded least squares on log-PSA residuals.
    """
    rng = np.random.default_rng(random_seed)

    # Filter measurements
    if cycle_nums is not None:
        raw_records = [m for m in patient.measurements if m.cycle in cycle_nums]
    else:
        raw_records = patient.measurements

    valid_records = [m for m in raw_records if m.psa is not None and m.psa >= 0.0]
    if len(valid_records) < 4:
        raise ValueError(
            f"Patient {patient.patient_id} has fewer than 4 valid PSA measurements."
        )

    t0 = raw_records[0].elapsed_days
    tx_schedule = _build_treatment_schedule(raw_records)

    t_obs = np.array([m.elapsed_days - t0 for m in valid_records], dtype=float)
    psa_obs = np.array([m.psa for m in valid_records], dtype=float)
    V_0 = max(1e-2, float(psa_obs[0]))

    # Load canonical bounds from model_params.json
    spec_params = load_model_params()
    r_S_range = spec_params["alpha1"]["range"]
    r_R_range = spec_params["alpha2"]["range"]
    k_S_range = spec_params["ES"]["range"]
    a_RS_range = spec_params["aRS"]["range"]
    a_SR_range = spec_params["aSR"]["range"]

    # Carrying capacity K: scaled to accommodate patient baseline
    K_val = max(200.0, 2.5 * float(np.max(psa_obs)))
    k_R_val = 0.0  # complete resistance to androgen ablation

    # Vector to fit: [r_S, r_R, k_S, a_RS, a_SR, f_R]
    param_names = ["alpha1", "alpha2", "ES", "aRS", "aSR", "f_R"]
    lb = np.array([
        r_S_range[0],
        r_R_range[0],
        k_S_range[0],
        a_RS_range[0],
        a_SR_range[0],
        1e-5,
    ], dtype=float)
    ub = np.array([
        r_S_range[1],
        r_R_range[1],
        k_S_range[1],
        a_RS_range[1],
        a_SR_range[1],
        0.20,
    ], dtype=float)

    def residuals(x: np.ndarray) -> np.ndarray:
        r_s, r_r, k_s, a_rs, a_sr, f_r = x
        _, s_pred, r_pred = simulate_lotka_volterra_psa(
            t_eval=t_obs,
            tx_schedule=tx_schedule,
            r_S=r_s,
            r_R=r_r,
            K=K_val,
            k_S=k_s,
            k_R=k_R_val,
            a_SR=a_sr,
            a_RS=a_rs,
            f_R=f_r,
            V_0=V_0,
        )
        pred_psa = np.maximum(EPSILON, s_pred + r_pred)
        return np.log(psa_obs + EPSILON) - np.log(pred_psa)

    best_res = None
    best_loss = float("inf")

    # Canonical initial guess from default values
    canonical_x0 = np.array([
        spec_params["alpha1"]["value"],
        spec_params["alpha2"]["value"],
        spec_params["ES"]["value"],
        spec_params["aRS"]["value"],
        spec_params["aSR"]["value"],
        0.005,
    ], dtype=float)

    candidate_x0s = [canonical_x0]
    for _ in range(n_restarts - 1):
        rand_x0 = lb + (ub - lb) * rng.uniform(0.05, 0.95, size=len(lb))
        candidate_x0s.append(rand_x0)

    for x0 in candidate_x0s:
        try:
            res = least_squares(
                residuals,
                x0,
                bounds=(lb, ub),
                ftol=1e-5,
                xtol=1e-5,
                gtol=1e-5,
                max_nfev=300,
            )
            curr_loss = float(np.sum(res.fun**2))
            if curr_loss < best_loss:
                best_loss = curr_loss
                best_res = res
        except Exception:
            continue

    if best_res is None:
        raise RuntimeError(f"Optimization failed for patient {patient.patient_id}")

    opt_x = best_res.x
    J = best_res.jac
    N = len(psa_obs)
    P = len(opt_x)

    # Condition number of Jacobian
    cond_number = float(np.linalg.cond(J))

    # Covariance & 95% Confidence Intervals
    s_sq = float(np.sum(best_res.fun**2) / max(1, N - P))
    jtj = J.T @ J
    cov = s_sq * np.linalg.pinv(jtj)
    se = np.sqrt(np.maximum(0.0, np.diag(cov)))

    cis_95: Dict[str, Tuple[float, float]] = {}
    fitted_params: Dict[str, float] = {}
    for i, name in enumerate(param_names):
        fitted_params[name] = float(opt_x[i])
        lower_bound = float(max(lb[i], opt_x[i] - 1.96 * se[i]))
        upper_bound = float(min(ub[i], opt_x[i] + 1.96 * se[i]))
        cis_95[name] = (round(lower_bound, 6), round(upper_bound, 6))

    # Parameter correlation matrix
    diag_se = np.sqrt(np.maximum(1e-12, np.diag(cov)))
    outer_se = np.outer(diag_se, diag_se)
    corr_mat = cov / outer_se
    np.fill_diagonal(corr_mat, 1.0)
    corr_mat = np.clip(corr_mat, -1.0, 1.0)

    collinear_pairs: List[Dict[str, Any]] = []
    unidentifiable_set = set()

    for i in range(P):
        for j in range(i + 1, P):
            val = float(corr_mat[i, j])
            if abs(val) > 0.90:
                collinear_pairs.append({
                    "param1": param_names[i],
                    "param2": param_names[j],
                    "correlation": round(val, 4),
                })
                unidentifiable_set.add(param_names[i])
                unidentifiable_set.add(param_names[j])

    # Profile likelihood for key parameters: alpha1 (r_S), alpha2 (r_R), aRS
    profile_results: Dict[str, Dict[str, Any]] = {}
    key_params_for_profile = ["alpha1", "alpha2", "aRS"]

    if run_profile_likelihood:
        for p_key in key_params_for_profile:
            p_idx = param_names.index(p_key)
            opt_val = opt_x[p_idx]
            # Grid of 5 points spanning 50% to 150% of optimum within bounds
            grid_min = max(lb[p_idx], 0.5 * opt_val)
            grid_max = min(ub[p_idx], 1.5 * opt_val)
            if grid_max <= grid_min:
                grid = [opt_val]
            else:
                grid = np.linspace(grid_min, grid_max, 5).tolist()

            losses = []
            other_indices = [k for k in range(P) if k != p_idx]
            lb_sub = lb[other_indices]
            ub_sub = ub[other_indices]

            for g_val in grid:
                def sub_residuals(sub_x: np.ndarray) -> np.ndarray:
                    full_x = np.zeros(P)
                    full_x[p_idx] = g_val
                    full_x[other_indices] = sub_x
                    return residuals(full_x)

                sub_x0 = opt_x[other_indices]
                try:
                    sub_fit = least_squares(
                        sub_residuals,
                        sub_x0,
                        bounds=(lb_sub, ub_sub),
                        ftol=1e-4,
                        xtol=1e-4,
                        max_nfev=60,
                    )
                    losses.append(float(np.sum(sub_fit.fun**2)))
                except Exception:
                    losses.append(float("inf"))

            valid_losses = [l for l in losses if np.isfinite(l)]
            if valid_losses and min(valid_losses) > 0:
                rel_var = float((max(valid_losses) - min(valid_losses)) / min(valid_losses))
            else:
                rel_var = 0.0

            is_flat = bool(rel_var < 0.08)
            if is_flat:
                unidentifiable_set.add(p_key)

            profile_results[p_key] = {
                "grid": [round(g, 6) for g in grid],
                "losses": [round(l, 6) for l in losses],
                "relative_variation": round(rel_var, 4),
                "is_flat": is_flat,
            }

    # Generate fine trajectories for output
    _, s_fitted, r_fitted = simulate_lotka_volterra_psa(
        t_eval=t_obs,
        tx_schedule=tx_schedule,
        r_S=opt_x[0],
        r_R=opt_x[1],
        K=K_val,
        k_S=opt_x[2],
        k_R=k_R_val,
        a_SR=opt_x[4],
        a_RS=opt_x[3],
        f_R=opt_x[5],
        V_0=V_0,
    )
    pred_psa = s_fitted + r_fitted
    log_rmse = float(np.sqrt(np.mean((np.log(psa_obs + EPSILON) - np.log(pred_psa + EPSILON))**2)))

    obs_records = [
        {"day": round(float(t_obs[i]), 1), "psa_obs": round(float(psa_obs[i]), 2)}
        for i in range(len(t_obs))
    ]
    pred_records = [
        {
            "day": round(float(t_obs[i]), 1),
            "psa_pred": round(float(pred_psa[i]), 2),
            "sensitive": round(float(s_fitted[i]), 2),
            "resistant": round(float(r_fitted[i]), 2),
        }
        for i in range(len(t_obs))
    ]

    return IASFitResult(
        patient_id=patient.patient_id,
        cohort=patient.cohort,
        log_psa_rmse=round(log_rmse, 4),
        fitted_parameters={k: round(v, 6) for k, v in fitted_params.items()},
        confidence_intervals_95=cis_95,
        condition_number=round(cond_number, 2),
        collinear_pairs=collinear_pairs,
        unidentifiable_parameters=sorted(list(unidentifiable_set)),
        profile_likelihoods=profile_results,
        parameter_correlation_matrix=[[round(float(c), 4) for c in row] for row in corr_mat],
        parameter_names=param_names,
        observed_psa=obs_records,
        predicted_psa=pred_records,
        random_seed=random_seed,
        n_restarts=n_restarts,
    )


def fit_ias_cohort(
    patients: List[IASPatient],
    max_patients: Optional[int] = None,
    cycle_nums: Optional[List[int]] = None,
    n_restarts: int = 20,
    random_seed: int = 42,
    run_profile_likelihood: bool = True,
) -> List[IASFitResult]:
    """
    Fits parameters and identifiability across a cohort of patients.
    """
    results: List[IASFitResult] = []
    cohort = patients[:max_patients] if max_patients else patients

    for p in cohort:
        try:
            res = fit_ias_patient(
                patient=p,
                cycle_nums=cycle_nums,
                n_restarts=n_restarts,
                random_seed=random_seed,
                run_profile_likelihood=run_profile_likelihood,
            )
            results.append(res)
        except Exception as err:
            print(f"[WARN] Skipping patient {p.patient_id}: {err}")
            continue

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Fit Lotka-Volterra model to Bruchovsky IAS data.")
    parser.add_argument("--patient-file", type=Path, help="Specific patient file path.")
    parser.add_argument("--patient-id", type=str, default="1", help="Patient ID to fit (default: 1).")
    parser.add_argument("--restarts", type=int, default=20, help="Number of random restarts (default: 20).")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42).")
    parser.add_argument("--cycle", type=int, default=1, help="Cycle number to fit (default: 1).")
    parser.add_argument("--output", type=Path, help="Path to save JSON fit result.")

    args = parser.parse_args()

    if args.patient_file:
        patient = load_ias_patient_from_file(args.patient_file)
    else:
        all_patients = load_all_ias_patients()
        matched = [p for p in all_patients if p.patient_id == str(args.patient_id)]
        if not matched:
            print(f"Patient {args.patient_id} not found in IAS dataset.")
            return 1
        patient = matched[0]

    cycle_filter = [args.cycle] if args.cycle > 0 else None
    print(f"Fitting Patient {patient.patient_id} (Cycle {args.cycle}, {args.restarts} restarts, seed={args.seed})...")

    fit_res = fit_ias_patient(
        patient=patient,
        cycle_nums=cycle_filter,
        n_restarts=args.restarts,
        random_seed=args.seed,
        run_profile_likelihood=True,
    )

    print("\n=== FIT RESULTS ===")
    print(f"Log-PSA RMSE: {fit_res.log_psa_rmse}")
    print(f"Condition Number: {fit_res.condition_number:.2e}")
    print("Fitted Parameters and 95% CIs:")
    for p_name, val in fit_res.fitted_parameters.items():
        ci = fit_res.confidence_intervals_95.get(p_name, (val, val))
        print(f"  {p_name}: {val:.5f} (95% CI: [{ci[0]:.5f}, {ci[1]:.5f}])")

    print("\nIdentifiability Findings:")
    print(f"  Unidentifiable Parameters: {fit_res.unidentifiable_parameters}")
    print("  Collinear Pairs (|r| > 0.90):")
    for pair in fit_res.collinear_pairs:
        print(f"    {pair['param1']} <-> {pair['param2']}: r = {pair['correlation']}")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w") as fp:
            json.dump(fit_res.to_dict(), fp, indent=2)
        print(f"Saved results to {args.output}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
