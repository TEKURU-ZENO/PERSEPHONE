import unittest
import numpy as np
from backend.python.compute.common.models.patient import PatientTwin
from backend.python.compute.optimization.environment.tumor_env import TumorEvolutionEnv
from backend.python.compute.optimization.environment.reward.composite import CompositeReward

class TestOncologyGymEnv(unittest.TestCase):
  def setUp(self):
    self.patient = PatientTwin(
      patient_id="patient-a",
      name="Elena Rostova",
      stage="Stage III",
      diagnosis="Ovarian Cancer",
      variants=[{"gene": "BRCA1", "variant": "c.1961delA"}],
      clinical_metrics={"renal": "eGFR: 88 (Normal)"}
    )

  def test_env_observation_shape(self):
    env = TumorEvolutionEnv(self.patient)
    obs = env.reset()
    self.assertEqual(len(obs), 6)
    self.assertEqual(obs.dtype, np.float32)

  def test_env_step_dosing_holiday(self):
    env = TumorEvolutionEnv(self.patient)
    obs = env.reset()
    # Action 0 (Holiday)
    next_obs, reward, done, info = env.step(0)
    self.assertEqual(len(next_obs), 6)
    self.assertEqual(info["actualDose"], 0.0)
    self.assertFalse(info["safetyOverride"])

  def test_env_reward_composite_math(self):
    # Total volume = 100, Toxicity = 0.6 (excess = 0.1), Alive = True, Dosing = False
    reward = CompositeReward.calculate(100.0, 0.6, True, False)
    # expected: tumor burden (-5.0) + toxicity excess (-1.0) + survival holiday (+1.5) = -4.5
    self.assertAlmostEqual(reward, -4.5)

  def test_env_safety_clearance_override(self):
    compromised_patient = PatientTwin(
      patient_id="patient-a",
      name="Elena",
      stage="Stage III",
      diagnosis="Ovarian Cancer",
      clinical_metrics={"renal": "eGFR: 32 mL/min/1.73m² (Severe decline)"}
    )
    env = TumorEvolutionEnv(compromised_patient)
    env.reset()
    # Action 4 (Full dose) should trigger safety filter override (renal clearance block)
    next_obs, reward, done, info = env.step(4)
    self.assertEqual(info["actualDose"], 0.0)
    self.assertTrue(info["safetyOverride"])
    self.assertTrue(any("Renal clearance safety limit exceeded" in v for v in info["violations"]))

if __name__ == '__main__':
  unittest.main()
