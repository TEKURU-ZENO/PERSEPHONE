"""
Scientific Unit Tests for Task B2: Lotka-Volterra Cross-Competition & LSODA Solver.
Verifies:
1. Step halving sensitivity (< 1 day TTP variation)
2. Non-negative volume invariants across full simulation timeline
3. Drug efficacy monotonicity (higher dose strictly decreases sensitive population)
4. RECIST 1.728x nadir and PCWG3 progression rule accuracy
"""
import unittest
from backend.python.compute.common.models.patient import PatientTwin
from backend.python.compute.simulation.solvers.lsoda_solver import simulate_lotka_volterra_lsoda
from backend.python.compute.simulation.rules.progression import (
    check_recist_progression,
    check_pcwg3_progression,
    check_simplified_progression
)

class TestLotkaVolterraModelCorrections(unittest.TestCase):
    def setUp(self):
        self.patient = PatientTwin(
            patient_id="patient-a",
            name="Elena Rostova",
            stage="Stage IIIC",
            diagnosis="High-Grade Serous Ovarian Cancer",
            model_params={
                "alpha1": 0.08,
                "alpha2": 0.045,
                "K": 200.0,
                "ES": 0.16,
                "ER": 0.015,
                "ke": 0.15,
                "beta": 0.25,
                "gamma": 0.10,
                "aSR": 1.0,
                "aRS": 1.0,
                "SS_init": 80.0,
                "SR_init": 2.0
            }
        )

    def test_step_halving_sensitivity(self):
        """Halving max_step from 0.5 to 0.25 must vary TTP by less than 1.0 day."""
        res_standard = simulate_lotka_volterra_lsoda(
            patient=self.patient,
            strategy="mtd",
            control_params={"duration": 180, "mtdDose": 10.0, "dosingInterval": 7.0},
            max_step=0.5,
            progression_rule="recist"
        )
        res_fine = simulate_lotka_volterra_lsoda(
            patient=self.patient,
            strategy="mtd",
            control_params={"duration": 180, "mtdDose": 10.0, "dosingInterval": 7.0},
            max_step=0.25,
            progression_rule="recist"
        )
        ttp_diff = abs(res_standard["timeToProgression"] - res_fine["timeToProgression"])
        self.assertLess(
            ttp_diff, 1.0,
            f"Step halving TTP difference must be < 1.0 day, got {ttp_diff:.4f} days"
        )

    def test_non_negative_volume_invariants(self):
        """All biological compartments must remain strictly non-negative at all times."""
        res = simulate_lotka_volterra_lsoda(
            patient=self.patient,
            strategy="adaptive",
            control_params={"duration": 180, "mtdDose": 15.0},
            max_step=0.5
        )
        for pt in res["timeline"]:
            self.assertGreaterEqual(pt["sensitive"], 0.0, f"Negative sensitive volume at day {pt['day']}")
            self.assertGreaterEqual(pt["resistant"], 0.0, f"Negative resistant volume at day {pt['day']}")
            self.assertGreaterEqual(pt["drugConcentration"], 0.0, f"Negative drug conc at day {pt['day']}")
            self.assertGreaterEqual(pt["toxicity"], 0.0, f"Negative toxicity at day {pt['day']}")

    def test_drug_kill_monotonicity(self):
        """Higher active drug dose must result in lower or equal sensitive population."""
        res_control = simulate_lotka_volterra_lsoda(
            patient=self.patient,
            strategy="control",
            control_params={"duration": 45}
        )
        res_high_dose = simulate_lotka_volterra_lsoda(
            patient=self.patient,
            strategy="mtd",
            control_params={"duration": 45, "mtdDose": 15.0}
        )
        # Sensitive volume under high dose should be less than control after initial cycle
        sens_treated = res_high_dose["timeline"][-1]["sensitive"]
        sens_control = res_control["timeline"][-1]["sensitive"]
        self.assertLess(
            sens_treated, sens_control,
            f"Treated sensitive cells ({sens_treated}) must be strictly less than control ({sens_control})"
        )

    def test_recist_progression_rule(self):
        """RECIST 1.1 3D volumetric threshold is exactly 1.728x nadir volume."""
        nadir = 10.0
        # 1.727x is below threshold
        self.assertFalse(check_recist_progression(17.27, nadir))
        # 1.728x is at threshold
        self.assertTrue(check_recist_progression(17.28, nadir))
        # 1.80x is above threshold
        self.assertTrue(check_recist_progression(18.0, nadir))

    def test_pcwg3_progression_rule(self):
        """PCWG3 requires >= 25% increase over nadir AND >= 2.0 ng/mL absolute increase."""
        nadir = 4.0
        # 25% of 4.0 is 1.0; 4.0 + 1.0 = 5.0 (increase is only 1.0 < 2.0 -> False)
        self.assertFalse(check_pcwg3_progression(5.0, nadir))
        # Absolute +2.0 is 6.0; 6.0 is 50% increase >= 25% AND +2.0 increase -> True
        self.assertTrue(check_pcwg3_progression(6.0, nadir))
        # Absolute 5.9 is +1.9 (< 2.0) -> False
        self.assertFalse(check_pcwg3_progression(5.9, nadir))

if __name__ == '__main__':
    unittest.main()
