"""
backend/python/tests/scientific/test_ias_dataset.py

Validates the integrity, schema, and loader functionality for the
Bruchovsky 2006 / Tanaka 2010 Intermittent Androgen Suppression (IAS)
real clinical oncology benchmark dataset.
"""

import sys
from pathlib import Path
import pytest

ROOT_DIR = Path(__file__).resolve().parents[4]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.python.compute.clinical_validation.calibration.ias_loader import (
    load_all_ias_patients,
    load_ias_patient_from_file,
    get_default_ias_data_dir,
    IASPatient,
    IASMeasurement,
)
from scripts.fetch_ias_data import (
    EXPECTED_SHA256,
    EXPECTED_BRUCHOVSKY_PATIENTS,
    EXPECTED_SHAW_PATIENTS,
    verify_extracted_data,
)


@pytest.fixture(scope="module")
def ias_data_dir():
    data_dir = get_default_ias_data_dir()
    if not data_dir.is_dir():
        pytest.skip("IAS benchmark data directory not found. Run scripts/fetch_ias_data.py first.")
    return data_dir


def test_ias_checksum_constant():
    """Confirms the expected SHA-256 matches the published Tanaka archive hash."""
    assert EXPECTED_SHA256 == "845683954e99253ddf68e488a48223e89c19247a92aec27daa79130d8f46904f"
    assert EXPECTED_BRUCHOVSKY_PATIENTS == 72
    assert EXPECTED_SHAW_PATIENTS == 18


def test_ias_directory_verification(ias_data_dir):
    """Verifies that the extracted directory matches patient count expectations."""
    is_valid, msg = verify_extracted_data(ias_data_dir)
    assert is_valid is True, f"Verification failed: {msg}"


def test_load_all_patients(ias_data_dir):
    """Verifies that all 90 patients (72 Bruchovsky + 18 Shaw) load cleanly."""
    patients = load_all_ias_patients(ias_data_dir)
    assert len(patients) == 90

    bruchovsky = [p for p in patients if p.cohort == "Bruchovsky_et_al"]
    shaw = [p for p in patients if p.cohort == "Shaw_et_al"]

    assert len(bruchovsky) == 72
    assert len(shaw) == 18


def test_patient_measurement_schema_and_integrity(ias_data_dir):
    """Verifies that patient measurements follow expected clinical and numerical invariants."""
    patient1_path = ias_data_dir / "Bruchovsky_et_al" / "patient001.txt"
    p1 = load_ias_patient_from_file(patient1_path, cohort="Bruchovsky_et_al")

    assert p1.patient_id == "1"
    assert p1.cohort == "Bruchovsky_et_al"
    assert len(p1.measurements) > 20
    assert len(p1.cycles) >= 2

    # Invariant: elapsed days should be non-decreasing
    elapsed = [m.elapsed_days for m in p1.measurements]
    assert all(elapsed[i] <= elapsed[i + 1] for i in range(len(elapsed) - 1))

    # Invariant: treatment_status should be 0 or 1
    for m in p1.measurements:
        assert m.treatment_status in (0, 1)
        assert m.cycle >= 1
        if m.psa is not None:
            assert m.psa >= 0.0

    # Invariant: Cycle filtering helper
    cycle1 = p1.get_cycle_measurements(1)
    assert len(cycle1) > 0
    assert all(m.cycle == 1 for m in cycle1)

    # Invariant: Valid PSA helper
    valid_psa = p1.get_valid_psa_measurements(1)
    assert len(valid_psa) > 0
    assert all(m.psa is not None for m in valid_psa)


def test_cohort_cycle_availability(ias_data_dir):
    """Verifies that at least 85 patients have >= 2 treatment cycles available for benchmark."""
    patients = load_all_ias_patients(ias_data_dir)
    multi_cycle_patients = [p for p in patients if len(p.cycles) >= 2]
    # In Bruchovsky dataset, 88 of 90 patients completed >= 2 cycles
    assert len(multi_cycle_patients) == 88
