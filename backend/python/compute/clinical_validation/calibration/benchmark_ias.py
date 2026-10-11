"""
backend/python/compute/clinical_validation/calibration/benchmark_ias.py

Cycle 1 -> Cycle 2 Out-of-Sample Prediction Benchmark on Bruchovsky IAS Clinical Data
(Task B5: Evaluates predictive validity on authentic longitudinal prostate cancer patients).

Protocol:
  1. Train Lotka-Volterra mechanistic model on Cycle 1 (both on- and off-treatment phases).
  2. Forecast Cycle 2 using fitted parameters, Cycle 2 baseline PSA, and Cycle 2 treatment schedule.
  3. Compare against 3 clinical/statistical baselines:
       - Baseline 1: Last Value Carried Forward (LVCF / flat line)
       - Baseline 2: Linear Extrapolation from Cycle 1 end
       - Baseline 3: Single-population exponential growth/decay (no resistance, no competition)
  4. Evaluate metrics across patients:
       - Log-PSA RMSE
       - Peak PSA MAPE (%)
       - Time to Nadir Prediction Error (days)
       - Time to PCWG3 Progression Prediction Error (days: 1.25x nadir AND +2.0 ng/mL)
  5. Report median and IQR [25th, 75th percentiles] for each model.
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

from backend.python.compute.clinical_validation.calibration.fit_ias import (
    EPSILON,
    _build_treatment_schedule,
    fit_ias_patient,
    simulate_lotka_volterra_psa,
)
from backend.python.compute.clinical_validation.calibration.ias_loader import (
    IASMeasurement,
    IASPatient,
    load_all_ias_patients,
    load_ias_patient_from_file,
)
from backend.python.compute.simulation.rules.progression import check_pcwg3_progression


@dataclass
class ModelMetrics:
    model_name: str
    log_psa_rmse: float
    peak_psa_mape: float
    time_to_nadir_error_days: float
    time_to_progression_error_days: float
    predicted_peak_psa: float
    observed_peak_psa: float
    predicted_time_to_nadir: float
    observed_time_to_nadir: float
    predicted_time_to_progression: float
    observed_time_to_progression: float


@dataclass
class PatientBenchmarkResult:
    patient_id: str
    cohort: str
    cycle1_data_points: int
    cycle2_data_points: int
    cycle2_duration_days: float
    models: Dict[str, ModelMetrics] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MetricSummary:
    median: float
    iqr_25: float
    iqr_75: float


@dataclass
class CohortBenchmarkSummary:
    total_evaluated_patients: int
    summary_by_model: Dict[str, Dict[str, MetricSummary]]
    patient_results: List[PatientBenchmarkResult]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _simulate_single_pop(
    t_eval: np.ndarray,
    tx_schedule: List[Tuple[float, float, int]],
    r: float,
    k: float,
    K: float,
    V_0: float,
) -> np.ndarray:
    """Simulates single-population logistic growth with linear drug kill."""
    curr = max(0.0, float(V_0))
    t_out: List[float] = []
    v_out: List[float] = []

    for k_idx, (t_start, t_end, tx) in enumerate(tx_schedule):
        is_last = k_idx == len(tx_schedule) - 1
        if is_last:
            pts = t_eval[(t_eval >= t_start - 1e-9) & (t_eval <= t_end + 1e-9)]
        else:
            pts = t_eval[(t_eval >= t_start - 1e-9) & (t_eval < t_end - 1e-9)]

        def rhs(t: float, y: np.ndarray) -> List[float]:
            v = max(0.0, float(y[0]))
            return [r * v * (1.0 - v / K) - k * tx * v]

        if len(pts) == 0:
            sol = solve_ivp(rhs, (t_start, t_end), [curr], method="RK45", rtol=1e-5, atol=1e-7)
            curr = max(0.0, float(sol.y[0][-1]))
            continue

        eval_grid = np.unique(np.concatenate([[t_start, t_end], pts]))
        sol = solve_ivp(rhs, (t_start, t_end), [curr], method="RK45", t_eval=eval_grid, rtol=1e-5, atol=1e-7)

        for p in pts:
            idx = int(np.argmin(np.abs(sol.t - p)))
            t_out.append(float(p))
            v_out.append(max(0.0, float(sol.y[0][idx])))

        curr = max(0.0, float(sol.y[0][-1]))

    order = np.argsort(t_out)
    return np.array(v_out)[order]


def _evaluate_progression_time(
    t_days: np.ndarray,
    psa_values: np.ndarray,
    duration: float,
) -> Tuple[float, float]:
    """
    Computes time to nadir and time to PCWG3 progression.
    Returns: (time_to_nadir, time_to_progression)
    """
    if len(psa_values) == 0:
        return 0.0, duration

    nadir_idx = int(np.argmin(psa_values))
    t_nadir = float(t_days[nadir_idx])
    nadir_val = float(psa_values[nadir_idx])

    t_prog = duration
    for i in range(nadir_idx + 1, len(psa_values)):
        if check_pcwg3_progression(float(psa_values[i]), nadir_val):
            t_prog = float(t_days[i])
            break

    return t_nadir, t_prog


def benchmark_patient_cycle2(
    patient: IASPatient,
    n_restarts: int = 15,
    random_seed: int = 42,
) -> Optional[PatientBenchmarkResult]:
    """
    Fits on Cycle 1 and predicts Cycle 2 across all 4 models for a single patient.
    """
    c1_records = [m for m in patient.measurements if m.cycle == 1]
    c2_records = [m for m in patient.measurements if m.cycle == 2]

    c1_valid = [m for m in c1_records if m.psa is not None and m.psa >= 0.0]
    c2_valid = [m for m in c2_records if m.psa is not None and m.psa >= 0.0]

    if len(c1_valid) < 4 or len(c2_valid) < 4:
        return None

    # Time zero for Cycle 2
    t0_c2 = c2_records[0].elapsed_days
    t_c2 = np.array([m.elapsed_days - t0_c2 for m in c2_valid], dtype=float)
    psa_c2_obs = np.array([m.psa for m in c2_valid], dtype=float)
    sched_c2 = _build_treatment_schedule(c2_records)
    c2_duration = float(t_c2[-1]) if len(t_c2) > 0 else 1.0

    peak_c2_obs = float(np.max(psa_c2_obs))
    t_nadir_obs, t_prog_obs = _evaluate_progression_time(t_c2, psa_c2_obs, c2_duration)

    V0_c2 = max(1e-2, float(psa_c2_obs[0]))
    K_val = max(200.0, 2.5 * peak_c2_obs)

    # 1. Fit Lotka-Volterra Model on Cycle 1
    fit_c1 = fit_ias_patient(
        patient=patient,
        cycle_nums=[1],
        n_restarts=n_restarts,
        random_seed=random_seed,
        run_profile_likelihood=False,
    )
    p_fit = fit_c1.fitted_parameters

    # Predict Cycle 2 with Lotka-Volterra Model
    _, s_c2_pred, r_c2_pred = simulate_lotka_volterra_psa(
        t_eval=t_c2,
        tx_schedule=sched_c2,
        r_S=p_fit["alpha1"],
        r_R=p_fit["alpha2"],
        K=K_val,
        k_S=p_fit["ES"],
        k_R=0.0,
        a_SR=p_fit["aSR"],
        a_RS=p_fit["aRS"],
        f_R=p_fit["f_R"],
        V_0=V0_c2,
    )
    pred_c2_lv = np.maximum(EPSILON, s_c2_pred + r_c2_pred)

    # 2. Baseline 1: Last Value Carried Forward (LVCF)
    lvcf_val = float(c1_valid[-1].psa)
    pred_c2_lvcf = np.full_like(psa_c2_obs, max(EPSILON, lvcf_val))

    # 3. Baseline 2: Linear Extrapolation from Cycle 1 end
    c1_off = [m for m in c1_valid if m.treatment_status == 0]
    if len(c1_off) >= 2 and (c1_off[-1].elapsed_days - c1_off[0].elapsed_days) > 1.0:
        slope = (c1_off[-1].psa - c1_off[0].psa) / (c1_off[-1].elapsed_days - c1_off[0].elapsed_days)
    else:
        slope = (c1_valid[-1].psa - c1_valid[-2].psa) / max(1.0, c1_valid[-1].elapsed_days - c1_valid[-2].elapsed_days)
    t_c1_end = c1_valid[-1].elapsed_days
    dt_from_c1_end = np.array([m.elapsed_days - t_c1_end for m in c2_valid], dtype=float)
    pred_c2_linear = np.maximum(EPSILON, lvcf_val + slope * dt_from_c1_end)

    # 4. Baseline 3: Single-Population Exponential Growth/Decay
    t0_c1 = c1_records[0].elapsed_days
    t_c1 = np.array([m.elapsed_days - t0_c1 for m in c1_valid], dtype=float)
    psa_c1 = np.array([m.psa for m in c1_valid], dtype=float)
    sched_c1 = _build_treatment_schedule(c1_records)
    V0_c1 = max(1e-2, float(psa_c1[0]))

    def single_res(x: np.ndarray) -> np.ndarray:
        pred = _simulate_single_pop(t_c1, sched_c1, x[0], x[1], K_val, V0_c1)
        return np.log(psa_c1 + EPSILON) - np.log(np.maximum(EPSILON, pred))

    opt_single = least_squares(
        single_res,
        [0.05, 0.10],
        bounds=([0.005, 0.005], [0.25, 0.50]),
        max_nfev=100,
    )
    pred_c2_single = np.maximum(
        EPSILON,
        _simulate_single_pop(t_c2, sched_c2, opt_single.x[0], opt_single.x[1], K_val, V0_c2)
    )

    # Metric evaluation function
    def compute_metrics(model_name: str, pred_curve: np.ndarray) -> ModelMetrics:
        rmse = float(np.sqrt(np.mean((np.log(psa_c2_obs + EPSILON) - np.log(pred_curve + EPSILON))**2)))
        peak_pred = float(np.max(pred_curve))
        mape_peak = float(abs(peak_pred - peak_c2_obs) / max(1e-2, peak_c2_obs) * 100.0)
        t_nadir_pred, t_prog_pred = _evaluate_progression_time(t_c2, pred_curve, c2_duration)
        nadir_err = float(abs(t_nadir_pred - t_nadir_obs))
        prog_err = float(abs(t_prog_pred - t_prog_obs))

        return ModelMetrics(
            model_name=model_name,
            log_psa_rmse=round(rmse, 4),
            peak_psa_mape=round(mape_peak, 2),
            time_to_nadir_error_days=round(nadir_err, 1),
            time_to_progression_error_days=round(prog_err, 1),
            predicted_peak_psa=round(peak_pred, 2),
            observed_peak_psa=round(peak_c2_obs, 2),
            predicted_time_to_nadir=round(t_nadir_pred, 1),
            observed_time_to_nadir=round(t_nadir_obs, 1),
            predicted_time_to_progression=round(t_prog_pred, 1),
            observed_time_to_progression=round(t_prog_obs, 1),
        )

    model_dict = {
        "Lotka-Volterra": compute_metrics("Lotka-Volterra", pred_c2_lv),
        "LVCF": compute_metrics("LVCF", pred_c2_lvcf),
        "Linear Extrapolation": compute_metrics("Linear Extrapolation", pred_c2_linear),
        "Single Exponential": compute_metrics("Single Exponential", pred_c2_single),
    }

    return PatientBenchmarkResult(
        patient_id=patient.patient_id,
        cohort=patient.cohort,
        cycle1_data_points=len(c1_valid),
        cycle2_data_points=len(c2_valid),
        cycle2_duration_days=round(c2_duration, 1),
        models=model_dict,
    )


def run_cohort_benchmark(
    patients: List[IASPatient],
    max_patients: Optional[int] = None,
    n_restarts: int = 15,
    random_seed: int = 42,
) -> CohortBenchmarkSummary:
    """
    Runs the prediction benchmark across all patients with >= 2 cycles.
    """
    eligible = [p for p in patients if len(p.cycles) >= 2]
    if max_patients:
        eligible = eligible[:max_patients]

    results: List[PatientBenchmarkResult] = []
    print(f"Executing Cycle 1 -> Cycle 2 Prediction Benchmark on {len(eligible)} eligible patients...")

    for i, p in enumerate(eligible):
        try:
            res = benchmark_patient_cycle2(p, n_restarts=n_restarts, random_seed=random_seed + i)
            if res:
                results.append(res)
                print(f"  [{len(results)}/{len(eligible)}] Pt {p.patient_id} ({p.cohort}) - LV RMSE: {res.models['Lotka-Volterra'].log_psa_rmse:.3f}")
        except Exception as e:
            print(f"  [WARN] Failed Pt {p.patient_id}: {e}")
            continue

    if not results:
        raise RuntimeError("No patients successfully evaluated in benchmark.")

    # Compute Median and IQR [25th, 75th] for each model and metric
    models_to_summarize = ["Lotka-Volterra", "LVCF", "Linear Extrapolation", "Single Exponential"]
    metric_keys = [
        "log_psa_rmse",
        "peak_psa_mape",
        "time_to_nadir_error_days",
        "time_to_progression_error_days",
    ]

    summary_by_model: Dict[str, Dict[str, MetricSummary]] = {}

    for m_name in models_to_summarize:
        summary_by_model[m_name] = {}
        for m_key in metric_keys:
            vals = [getattr(r.models[m_name], m_key) for r in results]
            q25, med, q75 = np.percentile(vals, [25, 50, 75])
            summary_by_model[m_name][m_key] = MetricSummary(
                median=round(float(med), 3),
                iqr_25=round(float(q25), 3),
                iqr_75=round(float(q75), 3),
            )

    return CohortBenchmarkSummary(
        total_evaluated_patients=len(results),
        summary_by_model=summary_by_model,
        patient_results=results,
    )


def format_benchmark_markdown_table(summary: CohortBenchmarkSummary) -> str:
    """Formats the comparative benchmark metrics into GitHub markdown table."""
    lines = [
        f"### Prediction Benchmark: Cycle 1 -> Cycle 2 Out-of-Sample Performance",
        f"*(Evaluated on N = {summary.total_evaluated_patients} authentic Bruchovsky 2006 / Tanaka 2010 IAS patients with $\\ge 2$ complete cycles)*\n",
        "| Model Architecture | Log-PSA RMSE (Median [IQR]) | Peak PSA MAPE % (Median [IQR]) | Time to Nadir Error Days (Median [IQR]) | Time to Progression Error Days (Median [IQR]) |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]

    for m_name, metrics in summary.summary_by_model.items():
        rmse = f"{metrics['log_psa_rmse'].median:.3f} [{metrics['log_psa_rmse'].iqr_25:.3f}, {metrics['log_psa_rmse'].iqr_75:.3f}]"
        mape = f"{metrics['peak_psa_mape'].median:.1f}% [{metrics['peak_psa_mape'].iqr_25:.1f}%, {metrics['peak_psa_mape'].iqr_75:.1f}%]"
        nadir = f"{metrics['time_to_nadir_error_days'].median:.1f} d [{metrics['time_to_nadir_error_days'].iqr_25:.1f}, {metrics['time_to_nadir_error_days'].iqr_75:.1f}]"
        prog = f"{metrics['time_to_progression_error_days'].median:.1f} d [{metrics['time_to_progression_error_days'].iqr_25:.1f}, {metrics['time_to_progression_error_days'].iqr_75:.1f}]"
        lines.append(f"| **{m_name}** | {rmse} | {mape} | {nadir} | {prog} |")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Cycle 1 -> Cycle 2 prediction benchmark.")
    parser.add_argument("--max-patients", type=int, default=None, help="Limit number of patients for quick testing.")
    parser.add_argument("--restarts", type=int, default=15, help="Number of random restarts per fit (default: 15).")
    parser.add_argument("--seed", type=int, default=42, help="Base random seed (default: 42).")
    parser.add_argument("--output-json", type=Path, help="Save detailed results JSON.")
    parser.add_argument("--output-md", type=Path, help="Save markdown table.")

    args = parser.parse_args()

    all_patients = load_all_ias_patients()
    summary = run_cohort_benchmark(
        patients=all_patients,
        max_patients=args.max_patients,
        n_restarts=args.restarts,
        random_seed=args.seed,
    )

    md_table = format_benchmark_markdown_table(summary)
    print("\n" + md_table + "\n")

    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output_json, "w") as fp:
            json.dump(summary.to_dict(), fp, indent=2)
        print(f"Saved JSON summary to {args.output_json}")

    if args.output_md:
        args.output_md.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output_md, "w") as fp:
            fp.write(md_table)
        print(f"Saved Markdown report to {args.output_md}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
