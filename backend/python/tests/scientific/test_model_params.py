"""
Unit test suite verifying Task B1 Central Parameter Source integrity.
Ensures research/model_params.json defines all 10 biophysical parameters,
validates deletion of legacy constants.py, and asserts removal of patient-a ternaries.
"""
import os
import json
import unittest
from backend.python.compute.simulation.params import load_model_params, get_default_model_params, REPO_ROOT
from backend.python.compute.common.models.patient import PatientTwin
from backend.python.compute.simulation.core.simulator import simulate_trajectory

class TestCentralModelParams(unittest.TestCase):
    def test_model_params_json_structure(self):
        """Verifies research/model_params.json contains all 10 required keys with metadata."""
        params = load_model_params()
        expected_keys = [
            "alpha1", "alpha2", "K", "ES", "ER", "ke", "beta", "gamma", "aSR", "aRS"
        ]
        for k in expected_keys:
            self.assertIn(k, params, f"Missing parameter {k} in model_params.json")
            entry = params[k]
            self.assertIn("value", entry)
            self.assertIn("unit", entry)
            self.assertIn("range", entry)
            self.assertIn("source_type", entry)
            self.assertIn("reference", entry)
            self.assertIsInstance(entry["value"], (int, float))
            self.assertIsInstance(entry["range"], list)
            self.assertEqual(len(entry["range"]), 2)

    def test_legacy_constants_file_deleted(self):
        """Verifies shared/math/constants.py is absent from the repository."""
        legacy_path = os.path.join(REPO_ROOT, "shared", "math", "constants.py")
        self.assertFalse(os.path.exists(legacy_path), "shared/math/constants.py must be deleted")

    def test_patient_twin_model_params_serialization(self):
        """Verifies PatientTwin correctly attaches and serializes modelParams."""
        twin = PatientTwin(
            patient_id="patient-a",
            name="Elena Rostova",
            stage="Stage IIIC",
            diagnosis="Ovarian Cancer",
            model_params={"alpha1": 0.08, "alpha2": 0.045, "K": 200.0, "SS_init": 80.0, "SR_init": 2.0}
        )
        data = twin.to_json()
        self.assertIn("modelParams", data)
        self.assertEqual(data["modelParams"]["alpha1"], 0.08)

        restored = PatientTwin.from_json(data)
        self.assertEqual(restored.model_params["K"], 200.0)

    def test_simulator_no_patient_ternary_literals(self):
        """Verifies simulator.py does not contain patient.patient_id == 'patient-a' ternaries."""
        sim_path = os.path.join(REPO_ROOT, "backend", "python", "compute", "simulation", "core", "simulator.py")
        with open(sim_path, "r", encoding="utf-8") as f:
            code = f.read()

        self.assertNotIn("patient.patient_id == 'patient-a'", code)
        self.assertNotIn("patient_id == 'patient-a'", code)

    def test_simulation_with_custom_model_params(self):
        """Verifies simulator respects patient-specific modelParams without hardcoded overrides."""
        twin_custom = PatientTwin(
            patient_id="custom-twin-001",
            name="Custom Virtual Twin",
            stage="Stage I",
            diagnosis="Synthetic",
            model_params={"alpha1": 0.05, "alpha2": 0.02, "K": 100.0, "SS_init": 50.0, "SR_init": 1.0}
        )
        res = simulate_trajectory(twin_custom, "mtd", {"duration": 14})
        self.assertEqual(res.timeline[0]["totalVolume"], 51.0)
        self.assertEqual(len(res.timeline), 29) # 14 days / 0.5 step + 1

if __name__ == '__main__':
    unittest.main()
