"""
backend/python/compute/clinical_validation/calibration/ias_loader.py

Loader and parser for the Intermittent Androgen Suppression (IAS) clinical
benchmark dataset (Bruchovsky et al., Cancer 2006; Tanaka et al., Phil. Trans. R. Soc. A 2010).

Dataset layout:
  data/ias_bruchovsky/
    ├── Bruchovsky_et_al/ (72 patients: patient001.txt .. patient072.txt)
    └── Shaw_et_al/       (18 patients: patient*.txt)

Columns per line (10 comma-separated values):
  0: patient_id        (integer / string ID)
  1: date              (YYYY/M/D HH:MM:SS)
  2: cpa_dose          (Cyproterone acetate dose, mg/day)
  3: leuprolide_dose   (Leuprolide dose, mg)
  4: psa               (Serum PSA, ng/mL)
  5: testosterone      (Serum testosterone, nmol/L)
  6: cycle             (Treatment cycle index, 1-indexed)
  7: treatment_status  (1 = on-treatment, 0 = off-treatment)
  8: julian_days       (Julian day counter)
  9: elapsed_days      (Elapsed days from cycle 1 baseline)
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Union


@dataclass
class IASMeasurement:
    patient_id: str
    date: str
    cpa_dose: float
    leuprolide_dose: float
    psa: Optional[float]
    testosterone: Optional[float]
    cycle: int
    treatment_status: int
    julian_days: float
    elapsed_days: float


@dataclass
class IASPatient:
    patient_id: str
    cohort: str
    filepath: Path
    measurements: List[IASMeasurement] = field(default_factory=list)

    @property
    def cycles(self) -> List[int]:
        return sorted(list({m.cycle for m in self.measurements}))

    @property
    def total_days(self) -> float:
        if not self.measurements:
            return 0.0
        return self.measurements[-1].elapsed_days - self.measurements[0].elapsed_days

    def get_cycle_measurements(self, cycle_num: int) -> List[IASMeasurement]:
        return [m for m in self.measurements if m.cycle == cycle_num]

    def get_valid_psa_measurements(self, cycle_num: Optional[int] = None) -> List[IASMeasurement]:
        records = (
            self.measurements
            if cycle_num is None
            else self.get_cycle_measurements(cycle_num)
        )
        return [m for m in records if m.psa is not None and m.psa >= 0.0]


def _safe_float(val: str) -> Optional[float]:
    val = val.strip().strip('"').strip("'")
    if not val:
        return None
    try:
        return float(val)
    except ValueError:
        return None


def _parse_measurement(row: List[str]) -> IASMeasurement:
    pid = row[0].strip().strip('"')
    date_str = row[1].strip().strip('"')
    cpa = _safe_float(row[2]) or 0.0
    leu = _safe_float(row[3]) or 0.0
    psa = _safe_float(row[4])
    testosterone = _safe_float(row[5])
    cycle = int(row[6].strip()) if row[6].strip().isdigit() else 1
    tx_status = int(row[7].strip()) if row[7].strip().isdigit() else 0
    julian = float(row[8].strip()) if row[8].strip() else 0.0
    elapsed = float(row[9].strip()) if row[9].strip() else 0.0

    return IASMeasurement(
        patient_id=pid,
        date=date_str,
        cpa_dose=cpa,
        leuprolide_dose=leu,
        psa=psa,
        testosterone=testosterone,
        cycle=cycle,
        treatment_status=tx_status,
        julian_days=julian,
        elapsed_days=elapsed,
    )


def load_ias_patient_from_file(filepath: Union[str, Path], cohort: str = "") -> IASPatient:
    p = Path(filepath)
    if not p.is_file():
        raise FileNotFoundError(f"IAS patient file not found: {p}")

    if not cohort:
        cohort = p.parent.name

    measurements: List[IASMeasurement] = []
    with open(p, "r", encoding="utf-8", errors="replace") as fp:
        reader = csv.reader(fp)
        for row in reader:
            if not row or len(row) < 10:
                continue
            measurements.append(_parse_measurement(row))

    patient_id = measurements[0].patient_id if measurements else p.stem
    return IASPatient(
        patient_id=patient_id,
        cohort=cohort,
        filepath=p,
        measurements=measurements,
    )


def get_default_ias_data_dir() -> Path:
    # Look relative to repository root
    repo_root = Path(__file__).resolve().parents[5]
    return repo_root / "data" / "ias_bruchovsky"


def load_all_ias_patients(data_dir: Optional[Union[str, Path]] = None) -> List[IASPatient]:
    target_dir = Path(data_dir) if data_dir else get_default_ias_data_dir()
    if not target_dir.is_dir():
        raise FileNotFoundError(
            f"IAS benchmark directory not found at {target_dir}. "
            "Please run 'python scripts/fetch_ias_data.py' to download."
        )

    patients: List[IASPatient] = []
    for cohort_name in ["Bruchovsky_et_al", "Shaw_et_al"]:
        cohort_dir = target_dir / cohort_name
        if cohort_dir.is_dir():
            for txt_file in sorted(cohort_dir.glob("*.txt")):
                patients.append(load_ias_patient_from_file(txt_file, cohort=cohort_name))

    return patients
