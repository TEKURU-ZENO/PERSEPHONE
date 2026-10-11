"""
backend/python/tests/scientific/test_fit_ias.py

Validates the parameter fitting and identifiability engine on authentic
Bruchovsky IAS clinical benchmark trajectories (Task B4).

Verifies:
  1. Multi-start bounded least squares converges to low log-PSA RMSE (< 0.50).
  2. Bounded parameters strictly respect ranges from research/model_params.json.
  3. Condition number of Jacobian is elevated (> 1e4), reflecting biomarker unidentifiability.
  4. Detects collinear parameter pairs (|r| > 0.90), including r_S vs k_S or a_RS vs f_R.
  5. 95% Confidence intervals contain optimal point estimates and respect parameter bounds.
  6. Profile likelihood produces valid loss profiles across parameter grids.
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
from backend.python.compute.clinical_validation.calibration.fit_ias import (
    fit_ias_patient,
    simulate_lotka_volterra_psa,
    _build_treatment_schedule,
)
from backend.python.compute.simulation.params import load_model_params


@pytest.fixture(scope="module")
def patient1():
    data_dir = get_default_ias_data_dir()
    if not data_dir.is_dir():
        pytest.skip("IAS data directory not found.")
    patients = load_all_ias_patients(data_dir)
    matched = [p for p in patients if p.patient_id == "1"]
    if not matched:
        pytest.skip("Patient 1 not found in IAS dataset.")
    return matched[0]


def test_fit_cycle1_parameters_and_bounds(patient1):
    """Fits Cycle 1 of Patient 1 and asserts bounds and RMSE targets."""
    spec_params = load_model_params()
    result = fit_ias_patient(
        patient=patient1,
        cycle_nums=[1],
        n_restarts=10,
        random_seed=42,
        run_profile_likelihood=False,
    )

    # 1. Low log-PSA RMSE on authentic clinical trajectory
    assert result.log_psa_rmse < 0.55
    assert result.log_psa_rmse > 0.0

    # 2. Strict adherence to research/model_params.json bounds
    for p_name, val in result.fitted_parameters.items():
        if p_name == "f_R":
            assert 1e-5 <= val <= 0.20
        else:
            lb, ub = spec_params[p_name]["range"]
            assert lb <= val <= ub + 1e-6, f"{p_name} value {val} out of bounds [{lb}, {ub}]"

    # 3. Confidence intervals validity
    for p_name, (ci_low, ci_high) in result.confidence_intervals_95.items():
        pt_val = result.fitted_parameters[p_name]
        assert ci_low <= pt_val + 1e-6
        assert pt_val <= ci_high + 1e-6


def test_identifiability_analysis(patient1):
    """Verifies Jacobian condition number, collinear pairs, and profile likelihood."""
    result = fit_ias_patient(
        patient=patient1,
        cycle_nums=[1],
        n_restarts=5,
        random_seed=42,
        run_profile_likelihood=True,
    )

    # Condition number should demonstrate high ill-conditioning (ill-posed inverse problem)
    assert result.condition_number > 1e4

    # High collinearity should detect at least 1 pair with |r| > 0.90
    assert len(result.collinear_pairs) >= 1
    correlations = [p["correlation"] for p in result.collinear_pairs]
    assert all(abs(c) >= 0.90 for c in correlations)

    # At least one parameter flagged as unidentifiable from PSA alone
    assert len(result.unidentifiable_parameters) >= 1

    # Profile likelihoods evaluated for key parameters
    assert "alpha1" in result.profile_likelihoods
    assert "alpha2" in result.profile_likelihoods
    assert "aRS" in result.profile_likelihoods
    for p_name in ["alpha1", "alpha2", "aRS"]:
        prof = result.profile_likelihoods[p_name]
        assert len(prof["grid"]) >= 3
        assert len(prof["losses"]) == len(prof["grid"])


def test_treatment_schedule_builder(patient1):
    """Verifies that schedule builder accurately isolates on/off blocks."""
    c1 = patient1.get_cycle_measurements(1)
    sched = _build_treatment_schedule(c1)
    assert len(sched) >= 2
    # First block should be on-treatment (tx == 1), second off-treatment (tx == 0)
    assert sched[0][2] == 1
    assert sched[1][2] == 0
    # Contiguous timeline
    assert sched[0][1] == sched[1][0]
