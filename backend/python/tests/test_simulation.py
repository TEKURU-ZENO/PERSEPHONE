import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from backend.python.compute.simulation.core.simulator import simulate_trajectory
from backend.python.compute.common.models.patient import PatientTwin

class TestSimulation(unittest.TestCase):
  def setUp(self):
    self.patient = PatientTwin(
      patient_id="patient-a",
      name="Elena",
      stage="Stage III",
      diagnosis="Ovarian"
    )

  def test_carrying_capacity_boundary(self):
    # Tumor volume should never exceed carrying capacity (K = 20000)
    result = simulate_trajectory(self.patient, "mtd", {"duration": 90, "mtdDose": 0.0})
    for pt in result.timeline:
      self.assertTrue(pt["totalVolume"] <= 20000.0)

  def test_drug_efficacy_decay(self):
    # Giving high drug dose should shrink tumor volume initially
    result_treated = simulate_trajectory(self.patient, "mtd", {"duration": 30, "mtdDose": 20.0})
    result_untreated = simulate_trajectory(self.patient, "mtd", {"duration": 30, "mtdDose": 0.0})
    
    last_treated = result_treated.timeline[-1]["totalVolume"]
    last_untreated = result_untreated.timeline[-1]["totalVolume"]
    
    self.assertTrue(last_treated < last_untreated)

if __name__ == '__main__':
  unittest.main()
