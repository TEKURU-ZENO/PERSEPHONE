import unittest
import numpy as np
from backend.python.compute.common.models.patient import PatientTwin
from backend.python.compute.clinical_validation.parameters.registry import ParameterRegistry
from backend.python.compute.clinical_validation.calibration.calibrator import fit_patient_parameters
from backend.python.compute.clinical_validation.validation.metrics import calculate_goodness_of_fit
from backend.python.compute.clinical_validation.sensitivity.local import run_local_sensitivity
from backend.python.compute.clinical_validation.uncertainty.samplers.monte_carlo import run_monte_carlo_uncertainty

class TestScientificValidation(unittest.TestCase):
  def setUp(self):
    self.patient = PatientTwin(
      patient_id="patient-a",
      name="Elena Rostova",
      stage="Stage III",
      diagnosis="Ovarian Cancer",
      clinical_metrics={"renal": "eGFR: 88 (Normal)"}
    )

  def test_parameter_registry_bounds(self):
    keys = ["K", "alpha1"]
    bounds = ParameterRegistry.get_bounds(keys)
    initials = ParameterRegistry.get_initials(keys)
    
    self.assertEqual(bounds[0], (100.0, 300.0))
    self.assertEqual(initials[1], 0.08)

  def test_goodness_of_fit_metrics(self):
    obs = [82.0, 76.5, 68.2]
    sim = [80.0, 75.0, 69.0]
    
    m = calculate_goodness_of_fit(obs, sim)
    self.assertTrue(m["rmse"] > 0)
    self.assertTrue(m["mae"] > 0)
    self.assertTrue(m["r2"] > 0.90)
    self.assertEqual(m["concordanceIndex"], 100.0)

  def test_calibration_minimizer_fit(self):
    # Setup empirical observed points
    empirical = [
      {"day": 0, "volume": 82.0},
      {"day": 7, "volume": 76.0},
      {"day": 14, "volume": 69.0}
    ]
    fit_res = fit_patient_parameters(self.patient, empirical)
    self.assertTrue(fit_res["success"])
    self.assertTrue(100.0 <= fit_res["calibratedParams"]["K"] <= 300.0)

  def test_local_sensitivity_derivatives(self):
    empirical = [
      {"day": 0, "volume": 82.0},
      {"day": 14, "volume": 69.0}
    ]
    sens = run_local_sensitivity(self.patient, empirical)
    self.assertTrue("K (Carrying Capacity)" in sens)
    self.assertTrue(sum(sens.values()) >= 99.0) # Sums to ~100%

  def test_monte_carlo_distribution_bands(self):
    fitted = {"K": 210.0, "alpha1": 0.075, "alpha2": 0.04}
    band = run_monte_carlo_uncertainty(self.patient, fitted, samples=10)
    self.assertEqual(len(band), 91) # Days 0 to 90
    first_pt = band[0]
    self.assertTrue(first_pt["lower"] <= first_pt["median"] <= first_pt["upper"])

if __name__ == '__main__':
  unittest.main()
