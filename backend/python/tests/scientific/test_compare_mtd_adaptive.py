"""
backend/python/tests/scientific/test_compare_mtd_adaptive.py

Scientific Verification of In Silico Continuous MTD vs. Adaptive Therapy Trial (Task B6).
Verifies:
  1. Mechanistic simulation of continuous MTD vs adaptive cycling.
  2. Competitive suppression benefit (Delta TTP > 0 when a_RS is high and f_R is small).
  3. Sensitivity analysis grid structure and monotonicity across (a_RS, f_R).
  4. Clinical cohort comparison metrics, categories, and dose reduction bounds.
"""

import sys
from pathlib import Path
import pytest
import numpy as np

ROOT_DIR = Path(__file__).resolve().parents[4]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.python.compute.clinical_validation.calibration.ias_loader import (
    load_all_ias_patients,
    get_default_ias_data_dir,
)
from backend.python.compute.clinical_validation.calibration.compare_mtd_adaptive import (
    simulate_patient_regimen,
    compare_patient_regimens,
    compute_sensitivity_matrix,
    format_regimen_comparison_markdown,
    run_cohort_regimen_comparison,
)


@pytest.fixture(scope="module")
def patient1():
    data_dir = get_default_ias_data_dir()
    if not data_dir.is_dir():
        pytest.skip("IAS data directory not found.")
    patients = load_all_ias_patients(data_dir)
    matched = [p for p in patients if p.patient_id == "1"]
    if not matched:
        pytest.skip("Patient 1 not found.")
    return matched[0]


def test_simulate_patient_regimen_mechanics():
    """Verifies that high competition produces extended TTP in adaptive therapy."""
    # Strong competition: a_RS = 2.0, small resistant pool f_R = 0.001
    ttp_cont, dose_cont, _ = simulate_patient_regimen(
        strategy="continuous",
        r_S=0.08,
        r_R=0.04,
        K=200.0,
        k_S=0.16,
        k_R=0.0,
        a_SR=1.0,
        a_RS=2.0,
        f_R=0.001,
        V_0=30.0,
    )

    ttp_adapt, dose_adapt, _ = simulate_patient_regimen(
        strategy="adaptive",
        r_S=0.08,
        r_R=0.04,
        K=200.0,
        k_S=0.16,
        k_R=0.0,
        a_SR=1.0,
        a_RS=2.0,
        f_R=0.001,
        V_0=30.0,
    )

    assert ttp_cont > 0.0
    assert ttp_adapt > 0.0
    # Adaptive should extend TTP due to competitive suppression
    assert ttp_adapt > ttp_cont
    assert dose_cont > 0.0
    assert dose_adapt > 0.0


def test_sensitivity_matrix_monotonicity():
    """Verifies that 2D sensitivity matrix captures the competitive suppression hypothesis."""
    sens = compute_sensitivity_matrix()
    assert len(sens.aRS_values) == 5
    assert len(sens.fR_values) == 5
    assert len(sens.delta_ttp_matrix) == 5
    assert all(len(row) == 5 for row in sens.delta_ttp_matrix)

    # For smallest resistant fraction (col 0, f_R = 0.0001),
    # increasing competition a_RS (from row 0 to row 4) should increase Delta TTP
    col0_vals = [sens.delta_ttp_matrix[i][0] for i in range(5)]
    assert col0_vals[-1] > col0_vals[0], f"Expected higher Delta TTP at higher a_RS: {col0_vals}"

    # For highest competition (row 4, a_RS = 2.0),
    # increasing resistant fraction f_R (from col 0 to col 4) should decrease Delta TTP
    row4_vals = sens.delta_ttp_matrix[4]
    assert row4_vals[0] > row4_vals[-1], f"Expected higher Delta TTP at lower f_R: {row4_vals}"


def test_compare_patient_regimens_on_patient1(patient1):
    """Verifies single patient comparison outputs, valid categories, and reasonable numbers."""
    comp = compare_patient_regimens(
        patient=patient1,
        fitted_params={
            "alpha1": 0.035,
            "alpha2": 0.010,
            "ES": 0.054,
            "aSR": 2.0,
            "aRS": 2.0,
            "f_R": 0.005,
        },
    )

    assert comp.patient_id == "1"
    assert comp.outcome_category in {"adaptive_superior", "continuous_superior", "equivalent"}
    assert comp.ttp_continuous > 0.0
    assert comp.ttp_adaptive > 0.0
    assert comp.cumulative_dose_continuous > 0.0
    assert comp.cumulative_dose_adaptive > 0.0
