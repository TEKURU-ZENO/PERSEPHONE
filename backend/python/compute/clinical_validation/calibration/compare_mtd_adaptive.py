"""
backend/python/compute/clinical_validation/calibration/compare_mtd_adaptive.py

In Silico Trial Comparison of Continuous MTD vs. Adaptive Therapy
using Fitted Lotka-Volterra Cross-Competition Parameters on Authentic Bruchovsky IAS Data
(Task B6: Evaluates evolutionary benefit, dose reduction, and competitive sensitivity).

Simulation Protocol:
  1. Continuous Maximum Tolerated Dose (MTD):
       - Drug applied continuously (u = 1.0) until progression.
  2. Adaptive Therapy (Evolutionary Cycling):
       - Drug applied until PSA drops to <= 50% of baseline.
       - Treatment paused (u = 0.0) until PSA rebounds to baseline (>= 100% of baseline).
       - Cycling repeated until progression.
  3. Progression Criterion:
       - PCWG3 guideline: >= 25% increase above nadir AND >= 2.0 ng/mL absolute increase,
         or failure to control above 125% of baseline.
  4. Sensitivity Analysis:
       - Evaluates delta TTP across a 2D parameter grid of
         interspecific competition a_RS in [0.2, 0.5, 1.0, 1.5, 2.0]
         and initial resistant fraction f_R in [0.0001, 0.001, 0.01, 0.05, 0.10].
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

from backend.python.compute.clinical_validation.calibration.fit_ias import (
    IASFitResult,
    fit_ias_patient,
)
from backend.python.compute.clinical_validation.calibration.ias_loader import (
    IASPatient,
    load_all_ias_patients,
)
from backend.python.compute.simulation.params import get_default_model_params
from backend.python.compute.simulation.rules.progression import check_pcwg3_progression


@dataclass
class PatientRegimenComparison:
    patient_id: str
    cohort: str
    ttp_continuous: float
    ttp_adaptive: float
    delta_ttp: float
    cumulative_dose_continuous: float
    cumulative_dose_adaptive: float
    dose_reduction_pct: float
    outcome_category: str
    parameters_used: Dict[str, float]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SensitivityAnalysisResult:
    aRS_values: List[float]
    fR_values: List[float]
    delta_ttp_matrix: List[List[float]]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CohortRegimenSummary:
    total_evaluated_patients: int
    fraction_adaptive_superior: float
    fraction_continuous_superior: float
    fraction_equivalent: float
    median_delta_ttp: float
    iqr_delta_ttp_25: float
    iqr_delta_ttp_75: float
    median_dose_reduction_pct: float
    iqr_dose_reduction_25: float
    iqr_dose_reduction_75: float
    sensitivity_analysis: SensitivityAnalysisResult
    patient_comparisons: List[PatientRegimenComparison]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def simulate_patient_regimen(
    strategy: str,
    r_S: float,
    r_R: float,
    K: float,
    k_S: float,
    k_R: float,
    a_SR: float,
    a_RS: float,
    f_R: float,
    V_0: float,
    unit_dose: float = 10.0,
    max_days: float = 2000.0,
    dt: float = 0.5,
) -> Tuple[float, float, float]:
    """
    Simulates Lotka-Volterra competition under MTD or Adaptive protocol.
    Returns: (time_to_progression_days, cumulative_dose, nadir_volume)
    """
    S = max(0.0, (1.0 - f_R) * V_0)
    R = max(0.0, f_R * V_0)
    t = 0.0

    days_on_tx = 0.0
    ttp = max_days
    nadir = V_0
    active_tx = True

    threshold_50 = 0.50 * V_0
    threshold_100 = 1.00 * V_0
    progression_cap = 1.25 * V_0

    while t < max_days:
        vol = S + R
        if vol < nadir:
            nadir = vol

        if strategy.lower() == "continuous":
            # Continuous MTD: check PCWG3 progression
            if t > 5.0 and check_pcwg3_progression(vol, nadir):
                ttp = t
                break
            u = 1.0
        elif strategy.lower() == "adaptive":
            # Adaptive therapy: treat to 50% drop, pause until 100% baseline rebound
            if active_tx:
                if vol <= threshold_50:
                    active_tx = False
                elif vol >= progression_cap:
                    ttp = t
                    break
                elif vol > 1.25 * nadir and vol >= nadir + 2.0 and vol > threshold_50:
                    # On-treatment failure to control
                    ttp = t
                    break
            else:
                if vol >= threshold_100:
                    active_tx = True
                    nadir = vol
                elif vol >= progression_cap:
                    ttp = t
                    break

            u = 1.0 if active_tx else 0.0
        else:
            raise ValueError(f"Unknown regimen strategy: {strategy}")

        if u > 0:
            days_on_tx += dt

        # Forward Euler with small step dt = 0.5 day
        ds = r_S * S * (1.0 - (S + a_SR * R) / K) - k_S * u * S
        dr = r_R * R * (1.0 - (R + a_RS * S) / K) - k_R * u * R

        S = max(0.0, S + ds * dt)
        R = max(0.0, R + dr * dt)
        t += dt

    cumulative_dose = days_on_tx * unit_dose
    return ttp, cumulative_dose, nadir


def compare_patient_regimens(
    patient: IASPatient,
    fitted_params: Optional[Dict[str, float]] = None,
    unit_dose: float = 10.0,
    max_days: float = 2000.0,
) -> PatientRegimenComparison:
    """
    Simulates continuous MTD vs adaptive therapy on fitted patient parameters.
    """
    if fitted_params is None:
        fit_res = fit_ias_patient(
            patient=patient,
            cycle_nums=[1],
            n_restarts=15,
            run_profile_likelihood=False,
        )
        fitted_params = fit_res.fitted_parameters

    valid_c1 = [m for m in patient.measurements if m.cycle == 1 and m.psa is not None and m.psa >= 0.0]
    V_0 = max(1.0, float(valid_c1[0].psa) if valid_c1 else 30.0)
    K_val = max(200.0, 2.5 * V_0)

    r_S = float(fitted_params.get("alpha1", 0.08))
    r_R = float(fitted_params.get("alpha2", 0.045))
    k_S = float(fitted_params.get("ES", 0.16))
    k_R = float(fitted_params.get("ER", 0.0))
    a_SR = float(fitted_params.get("aSR", 1.0))
    a_RS = float(fitted_params.get("aRS", 1.0))
    f_R = float(fitted_params.get("f_R", 0.005))

    ttp_cont, dose_cont, _ = simulate_patient_regimen(
        strategy="continuous",
        r_S=r_S,
        r_R=r_R,
        K=K_val,
        k_S=k_S,
        k_R=k_R,
        a_SR=a_SR,
        a_RS=a_RS,
        f_R=f_R,
        V_0=V_0,
        unit_dose=unit_dose,
        max_days=max_days,
    )

    ttp_adapt, dose_adapt, _ = simulate_patient_regimen(
        strategy="adaptive",
        r_S=r_S,
        r_R=r_R,
        K=K_val,
        k_S=k_S,
        k_R=k_R,
        a_SR=a_SR,
        a_RS=a_RS,
        f_R=f_R,
        V_0=V_0,
        unit_dose=unit_dose,
        max_days=max_days,
    )

    delta_ttp = round(ttp_adapt - ttp_cont, 1)
    if dose_cont > 0:
        dose_red = round((dose_cont - dose_adapt) / dose_cont * 100.0, 1)
    else:
        dose_red = 0.0

    if delta_ttp > 5.0:
        outcome = "adaptive_superior"
    elif delta_ttp < -5.0:
        outcome = "continuous_superior"
    else:
        outcome = "equivalent"

    return PatientRegimenComparison(
        patient_id=patient.patient_id,
        cohort=patient.cohort,
        ttp_continuous=round(ttp_cont, 1),
        ttp_adaptive=round(ttp_adapt, 1),
        delta_ttp=delta_ttp,
        cumulative_dose_continuous=round(dose_cont, 1),
        cumulative_dose_adaptive=round(dose_adapt, 1),
        dose_reduction_pct=dose_red,
        outcome_category=outcome,
        parameters_used={
            "alpha1": r_S,
            "alpha2": r_R,
            "ES": k_S,
            "aSR": a_SR,
            "aRS": a_RS,
            "f_R": f_R,
            "K": K_val,
            "V_0": V_0,
        },
    )


def compute_sensitivity_matrix(
    base_params: Optional[Dict[str, float]] = None,
    V_0: float = 30.0,
    K: float = 200.0,
) -> SensitivityAnalysisResult:
    """
    Computes sensitivity matrix of Delta TTP across competition a_RS and resistant fraction f_R.
    """
    defaults = get_default_model_params()
    base = base_params or {}

    r_S = float(base.get("alpha1", defaults["alpha1"]))
    r_R = float(base.get("alpha2", defaults["alpha2"]))
    k_S = float(base.get("ES", defaults["ES"]))
    k_R = float(base.get("ER", 0.0))
    a_SR = float(base.get("aSR", 1.0))

    aRS_values = [0.2, 0.5, 1.0, 1.5, 2.0]
    fR_values = [0.0001, 0.001, 0.01, 0.05, 0.10]
    matrix: List[List[float]] = []

    for a_rs in aRS_values:
        row: List[float] = []
        for f_r in fR_values:
            t_cont, _, _ = simulate_patient_regimen(
                strategy="continuous",
                r_S=r_S,
                r_R=r_R,
                K=K,
                k_S=k_S,
                k_R=k_R,
                a_SR=a_SR,
                a_RS=a_rs,
                f_R=f_r,
                V_0=V_0,
            )
            t_adapt, _, _ = simulate_patient_regimen(
                strategy="adaptive",
                r_S=r_S,
                r_R=r_R,
                K=K,
                k_S=k_S,
                k_R=k_R,
                a_SR=a_SR,
                a_RS=a_rs,
                f_R=f_r,
                V_0=V_0,
            )
            row.append(round(t_adapt - t_cont, 1))
        matrix.append(row)

    return SensitivityAnalysisResult(
        aRS_values=aRS_values,
        fR_values=fR_values,
        delta_ttp_matrix=matrix,
    )


def run_cohort_regimen_comparison(
    patients: List[IASPatient],
    max_patients: Optional[int] = None,
    n_restarts: int = 15,
    random_seed: int = 42,
) -> CohortRegimenSummary:
    """
    Runs the Continuous MTD vs Adaptive comparison across the cohort.
    """
    cohort = patients[:max_patients] if max_patients else patients
    comparisons: List[PatientRegimenComparison] = []

    print(f"Executing In Silico MTD vs Adaptive Comparison across {len(cohort)} patients...")
    for i, p in enumerate(cohort):
        try:
            fit_res = fit_ias_patient(
                patient=p,
                cycle_nums=[1],
                n_restarts=n_restarts,
                random_seed=random_seed + i,
                run_profile_likelihood=False,
            )
            comp = compare_patient_regimens(p, fitted_params=fit_res.fitted_parameters)
            comparisons.append(comp)
            print(f"  [{len(comparisons)}/{len(cohort)}] Pt {p.patient_id} - Delta TTP: {comp.delta_ttp:+.1f}d | Dose Red: {comp.dose_reduction_pct:.1f}%")
        except Exception as e:
            print(f"  [WARN] Failed Pt {p.patient_id}: {e}")
            continue

    if not comparisons:
        raise RuntimeError("No patients evaluated in cohort comparison.")

    n_tot = len(comparisons)
    n_adapt_sup = sum(1 for c in comparisons if c.outcome_category == "adaptive_superior")
    n_cont_sup = sum(1 for c in comparisons if c.outcome_category == "continuous_superior")
    n_equiv = sum(1 for c in comparisons if c.outcome_category == "equivalent")

    delta_ttps = [c.delta_ttp for c in comparisons]
    q25_ttp, med_ttp, q75_ttp = np.percentile(delta_ttps, [25, 50, 75])

    dose_reds = [c.dose_reduction_pct for c in comparisons]
    q25_dose, med_dose, q75_dose = np.percentile(dose_reds, [25, 50, 75])

    sensitivity = compute_sensitivity_matrix()

    return CohortRegimenSummary(
        total_evaluated_patients=n_tot,
        fraction_adaptive_superior=round(n_adapt_sup / n_tot, 3),
        fraction_continuous_superior=round(n_cont_sup / n_tot, 3),
        fraction_equivalent=round(n_equiv / n_tot, 3),
        median_delta_ttp=round(float(med_ttp), 1),
        iqr_delta_ttp_25=round(float(q25_ttp), 1),
        iqr_delta_ttp_75=round(float(q75_ttp), 1),
        median_dose_reduction_pct=round(float(med_dose), 1),
        iqr_dose_reduction_25=round(float(q25_dose), 1),
        iqr_dose_reduction_75=round(float(q75_dose), 1),
        sensitivity_analysis=sensitivity,
        patient_comparisons=comparisons,
    )


def format_regimen_comparison_markdown(summary: CohortRegimenSummary) -> str:
    """Formats the MTD vs Adaptive findings into a comprehensive markdown report."""
    sens = summary.sensitivity_analysis
    lines = [
        "### In Silico Trial: Continuous MTD vs. Evolutionary Adaptive Therapy",
        f"*(Evaluated across N = {summary.total_evaluated_patients} authentic Bruchovsky 2006 / Tanaka 2010 patients with fitted parameters)*\n",
        "#### 1. Cohort Outcome Distribution",
        f"- **Adaptive Therapy Superior ($\\Delta\\text{{TTP}} > +5\\text{{ days}}$):** {summary.fraction_adaptive_superior * 100:.1f}% of cohort",
        f"- **Continuous MTD Superior ($\\Delta\\text{{TTP}} < -5\\text{{ days}}$):** {summary.fraction_continuous_superior * 100:.1f}% of cohort",
        f"- **Equivalent Outcome ($|\\Delta\\text{{TTP}}| \\le 5\\text{{ days}}$):** {summary.fraction_equivalent * 100:.1f}% of cohort",
        f"- **Median TTP Difference (Adaptive - MTD):** {summary.median_delta_ttp:+.1f} days [IQR: {summary.iqr_delta_ttp_25:+.1f}, {summary.iqr_delta_ttp_75:+.1f} days]",
        f"- **Median Cumulative Dose Reduction:** {summary.median_dose_reduction_pct:.1f}% [IQR: {summary.iqr_dose_reduction_25:.1f}%, {summary.iqr_dose_reduction_75:.1f}%]\n",
        "#### 2. Competitive Suppression Sensitivity Grid ($\\Delta\\text{TTP}$ in Days)",
        "| Interspecific Competition ($a_{RS}$) | $f_R = 0.01\\%$ | $f_R = 0.1\\%$ | $f_R = 1.0\\%$ | $f_R = 5.0\\%$ | $f_R = 10.0\\%$ |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |",
    ]

    for i, a_val in enumerate(sens.aRS_values):
        row_str = f"| **$a_{{RS}} = {a_val:.1f}$** | " + " | ".join(f"{val:+.1f} d" for val in sens.delta_ttp_matrix[i]) + " |"
        lines.append(row_str)

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Continuous MTD vs Adaptive Therapy comparison on fitted parameters.")
    parser.add_argument("--max-patients", type=int, default=None, help="Limit number of patients for quick testing.")
    parser.add_argument("--restarts", type=int, default=15, help="Number of random restarts for fitting (default: 15).")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42).")
    parser.add_argument("--output-json", type=Path, help="Path to save output JSON.")
    parser.add_argument("--output-md", type=Path, help="Path to save output Markdown.")

    args = parser.parse_args()

    all_patients = load_all_ias_patients()
    summary = run_cohort_regimen_comparison(
        patients=all_patients,
        max_patients=args.max_patients,
        n_restarts=args.restarts,
        random_seed=args.seed,
    )

    md_report = format_regimen_comparison_markdown(summary)
    print("\n" + md_report + "\n")

    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output_json, "w") as fp:
            json.dump(summary.to_dict(), fp, indent=2)
        print(f"Saved results JSON to {args.output_json}")

    if args.output_md:
        args.output_md.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output_md, "w") as fp:
            fp.write(md_report)
        print(f"Saved Markdown report to {args.output_md}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
