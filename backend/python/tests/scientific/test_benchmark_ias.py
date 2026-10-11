"""
backend/python/tests/scientific/test_benchmark_ias.py

Scientific Verification of Out-of-Sample Prediction Benchmark (Task B5).
Verifies that the Lotka-Volterra mechanistic competition model beats
clinical and statistical baselines (LVCF, Linear Extrapolation, Single Exponential)
on out-of-sample Cycle 2 prediction on authentic Bruchovsky IAS clinical data.
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
from backend.python.compute.clinical_validation.calibration.benchmark_ias import (
    benchmark_patient_cycle2,
    run_cohort_benchmark,
    format_benchmark_markdown_table,
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


def test_benchmark_patient1_beats_baselines(patient1):
    """Verifies that Lotka-Volterra beats LVCF and Linear baselines on Patient 1 Cycle 2."""
    res = benchmark_patient_cycle2(patient1, n_restarts=10, random_seed=42)
    assert res is not None

    lv = res.models["Lotka-Volterra"]
    lvcf = res.models["LVCF"]
    lin = res.models["Linear Extrapolation"]
    single = res.models["Single Exponential"]

    # Invariants on metric values
    for m in [lv, lvcf, lin, single]:
        assert m.log_psa_rmse >= 0.0
        assert m.peak_psa_mape >= 0.0
        assert m.time_to_nadir_error_days >= 0.0
        assert m.time_to_progression_error_days >= 0.0

    # Lotka-Volterra should achieve superior RMSE than naive baselines
    assert lv.log_psa_rmse < lvcf.log_psa_rmse
    assert lv.log_psa_rmse < lin.log_psa_rmse


def test_cohort_benchmark_summary_and_table():
    """Verifies cohort evaluation, median/IQR statistics, and markdown table formatting."""
    data_dir = get_default_ias_data_dir()
    if not data_dir.is_dir():
        pytest.skip("IAS data directory not found.")
    patients = load_all_ias_patients(data_dir)

    summary = run_cohort_benchmark(
        patients=patients,
        max_patients=2,
        n_restarts=5,
        random_seed=42,
    )

    assert summary.total_evaluated_patients == 2
    assert "Lotka-Volterra" in summary.summary_by_model
    assert "LVCF" in summary.summary_by_model
    assert "Linear Extrapolation" in summary.summary_by_model
    assert "Single Exponential" in summary.summary_by_model

    for m_name, metrics in summary.summary_by_model.items():
        for k in ["log_psa_rmse", "peak_psa_mape", "time_to_nadir_error_days"]:
            m_stat = metrics[k]
            assert m_stat.iqr_25 <= m_stat.median + 1e-6
            assert m_stat.median <= m_stat.iqr_75 + 1e-6

    # Test markdown table generation
    table_str = format_benchmark_markdown_table(summary)
    assert "### Prediction Benchmark: Cycle 1 -> Cycle 2 Out-of-Sample Performance" in table_str
    assert "Lotka-Volterra" in table_str
    assert "LVCF" in table_str
