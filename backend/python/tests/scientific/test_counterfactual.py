"""
Unit tests for PERSEPHONE Counterfactual Research Platform (Phase 17).
Validates synthetic cohort generation, treatment matrix definition,
multi-arm RK4 mechanistic simulation, comparative survival analysis (Kaplan-Meier),
uncertainty quantification (95% CIs), causal provenance manifests, and comparator ranking.
"""
import unittest
from backend.python.compute.counterfactual.cohort import CohortMember, SyntheticCohort
from backend.python.compute.counterfactual.generator import SyntheticCohortGenerator
from backend.python.compute.counterfactual.treatment_matrix import TreatmentMatrix
from backend.python.compute.counterfactual.scenario import CounterfactualScenario
from backend.python.compute.counterfactual.simulator import CounterfactualSimulator
from backend.python.compute.counterfactual.outcomes import CounterfactualOutcomes
from backend.python.compute.counterfactual.uncertainty import CounterfactualUncertaintyEngine
from backend.python.compute.counterfactual.provenance import CausalProvenanceEngine
from backend.python.compute.counterfactual.comparison import CounterfactualComparator
from backend.python.compute.counterfactual.registry import CounterfactualRegistry


class TestCounterfactualPlatform(unittest.TestCase):
    """Test suite for all Phase 17 Counterfactual compute modules."""

    def setUp(self):
        self.patient_data = {
            "id": "patient-a",
            "name": "Elena Rostova",
            "tumor_volume": 82.0,
            "resistant_fraction": 0.05,
            "carrying_capacity": 200.0,
            "turnover_rate": 0.03,
            "sensitive_kill_rate": 0.04,
            "resistant_kill_rate": 0.005,
            "toxicity_clearance": 0.15,
            "drug_sensitivity_ic50": 1.5
        }

    def test_synthetic_cohort_generation(self):
        """Validates bounded parameter perturbation and reproducibility across synthetic digital twins."""
        cohort = SyntheticCohortGenerator.generate_cohort(
            patient_data=self.patient_data,
            cohort_size=25,
            seed=42,
            variance_scale=0.15
        )

        self.assertIsInstance(cohort, SyntheticCohort)
        self.assertEqual(cohort.size, 25)
        self.assertEqual(cohort.anchor_patient_id, "patient-a")
        self.assertEqual(len(cohort.members), 25)

        # Verify bounded parameters on every member
        for m in cohort.members:
            self.assertIsInstance(m, CohortMember)
            bp = m.biophysical_params
            self.assertGreaterEqual(bp["V0"], 10.0)
            self.assertLessEqual(bp["V0"], 500.0)
            self.assertGreaterEqual(bp["resistant_ratio"], 0.001)
            self.assertLessEqual(bp["resistant_ratio"], 0.5)
            self.assertGreater(bp["K"], 50.0)
            self.assertLessEqual(bp["K"], 500.0)
            self.assertGreater(bp["alpha1"], 0.0)
            self.assertGreater(bp["alpha2"], 0.0)
            self.assertGreater(bp["ES"], 0.0)
            self.assertGreater(bp["ER"], 0.0)

        # Verify statistical distribution summary
        dist = cohort.get_distribution_summary()
        self.assertIn("V0", dist)
        self.assertIn("resistant_ratio", dist)
        self.assertIn("mean", dist["V0"])
        self.assertIn("std", dist["V0"])
        self.assertIn("median", dist["V0"])

        # Test deterministic reproducibility with identical seed
        cohort_repro = SyntheticCohortGenerator.generate_cohort(
            patient_data=self.patient_data,
            cohort_size=25,
            seed=42,
            variance_scale=0.15
        )
        self.assertAlmostEqual(cohort.members[0].biophysical_params["V0"], cohort_repro.members[0].biophysical_params["V0"], places=4)

    def test_treatment_matrix_six_arms(self):
        """Verifies definition of the 6 standardized treatment arms and their regimen parameters."""
        arms = TreatmentMatrix.list_arm_ids()
        self.assertEqual(len(arms), 6)
        expected_arms = ["mtd", "monotherapy_alt", "adaptive", "metronomic", "trial_protocol", "combination"]
        for expected in expected_arms:
            self.assertIn(expected, arms)

        # Check regimen definitions
        for arm_id in expected_arms:
            regimen = TreatmentMatrix.get_regimen(arm_id)
            self.assertIsNotNone(regimen)
            self.assertIn("name", regimen)
            self.assertIn("category", regimen)
            self.assertIn("schedule_type", regimen)
            self.assertIn("description", regimen)

    def test_counterfactual_simulation_and_outcomes(self):
        """Tests multi-patient multi-arm RK4 mechanistic simulation and Kaplan-Meier outcome aggregation."""
        cohort = SyntheticCohortGenerator.generate_cohort(
            patient_data=self.patient_data,
            cohort_size=10,
            seed=123
        )

        scenario = CounterfactualScenario(
            scenario_id=f"scen-{cohort.cohort_id}",
            target_cohort=cohort,
            arms=["mtd", "adaptive"],
            duration=90,
            control_arm="mtd"
        )

        sim_output = CounterfactualSimulator.simulate_scenario(scenario)
        self.assertEqual(sim_output["scenario_id"], scenario.scenario_id)
        self.assertIn("mtd", sim_output["arm_results"])
        self.assertIn("adaptive", sim_output["arm_results"])
        self.assertEqual(len(sim_output["arm_results"]["mtd"]), 10)
        self.assertEqual(len(sim_output["arm_results"]["adaptive"]), 10)

        # Outcomes per arm
        outcomes_mtd = CounterfactualOutcomes.compute_arm_outcomes("mtd", sim_output["arm_results"]["mtd"], duration=90)
        self.assertIn("kaplan_meier_curve", outcomes_mtd)
        self.assertIn("median_pfs_days", outcomes_mtd)
        self.assertIn("objective_response_rate", outcomes_mtd)
        self.assertIn("disease_control_rate", outcomes_mtd)
        self.assertIn("mean_cumulative_dose", outcomes_mtd)
        self.assertIn("mean_cumulative_toxicity", outcomes_mtd)

        self.assertGreater(len(outcomes_mtd["kaplan_meier_curve"]), 0)
        self.assertGreaterEqual(outcomes_mtd["objective_response_rate"], 0.0)
        self.assertLessEqual(outcomes_mtd["objective_response_rate"], 1.0)

    def test_uncertainty_quantification_engine(self):
        """Validates 95% confidence interval estimation across comparative counterfactual metrics."""
        # Simulated digital twin paired records
        control_records = [
            {"ttp": 60, "cumulative_toxicity": 40.0, "cumulative_dose": 100.0, "resistance_emergence_day": 45},
            {"ttp": 65, "cumulative_toxicity": 42.0, "cumulative_dose": 100.0, "resistance_emergence_day": 50},
            {"ttp": 55, "cumulative_toxicity": 38.0, "cumulative_dose": 100.0, "resistance_emergence_day": 40},
            {"ttp": 70, "cumulative_toxicity": 45.0, "cumulative_dose": 100.0, "resistance_emergence_day": 55},
            {"ttp": 58, "cumulative_toxicity": 39.0, "cumulative_dose": 100.0, "resistance_emergence_day": 42}
        ]
        arm_records = [
            {"ttp": 90, "cumulative_toxicity": 22.0, "cumulative_dose": 60.0, "resistance_emergence_day": 75},
            {"ttp": 95, "cumulative_toxicity": 24.0, "cumulative_dose": 62.0, "resistance_emergence_day": 80},
            {"ttp": 85, "cumulative_toxicity": 20.0, "cumulative_dose": 58.0, "resistance_emergence_day": 70},
            {"ttp": 100, "cumulative_toxicity": 25.0, "cumulative_dose": 65.0, "resistance_emergence_day": 85},
            {"ttp": 88, "cumulative_toxicity": 21.0, "cumulative_dose": 59.0, "resistance_emergence_day": 72}
        ]

        uncertainty = CounterfactualUncertaintyEngine.estimate_comparison_uncertainty(control_records, arm_records)
        self.assertIn("ate_ttp_days", uncertainty)
        self.assertIn("delta_toxicity", uncertainty)
        self.assertIn("dose_reduction_percent", uncertainty)
        self.assertIn("therapeutic_efficiency_index", uncertainty)

        ate = uncertainty["ate_ttp_days"]
        self.assertEqual(ate["uncertainty"]["ci_level"], 0.95)
        self.assertGreater(ate["value"], 0.0) # Adaptive delayed progression
        self.assertLessEqual(ate["uncertainty"]["lower_bound"], ate["value"])
        self.assertGreaterEqual(ate["uncertainty"]["upper_bound"], ate["value"])

        delta_tox = uncertainty["delta_toxicity"]
        self.assertLess(delta_tox["value"], 0.0) # Adaptive reduced toxicity
        self.assertLessEqual(delta_tox["uncertainty"]["lower_bound"], delta_tox["value"])
        self.assertGreaterEqual(delta_tox["uncertainty"]["upper_bound"], delta_tox["value"])

    def test_causal_provenance_and_assumptions(self):
        """Validates research-grade reproducibility IDs and causal assumption manifest."""
        manifest = CausalProvenanceEngine.generate_reproducibility_manifest(
            anchor_patient_id="patient-a",
            cohort_seed=42,
            simulation_seed=42,
            arms=["mtd", "adaptive", "metronomic"],
            biophysical_params=self.patient_data
        )

        self.assertTrue(manifest["experiment_id"].startswith("exp-cf-"))
        self.assertEqual(manifest["anchor_patient_id"], "patient-a")
        self.assertEqual(manifest["cohort_seed"], 42)
        self.assertEqual(manifest["simulation_seed"], 42)
        self.assertEqual(manifest["reproducibility_status"], "deterministic")
        self.assertIn("parameter_hash", manifest)
        self.assertIn("regimen_hash", manifest)

        causal_manifest = CausalProvenanceEngine.generate_causal_manifest("mtd", "adaptive")
        self.assertEqual(causal_manifest["control_arm"], "mtd")
        self.assertEqual(causal_manifest["intervention_arm"], "adaptive")
        self.assertIn("assumptions", causal_manifest)
        self.assertGreater(len(causal_manifest["assumptions"]), 0)
        self.assertIn("disclaimer", causal_manifest)

    def test_counterfactual_comparator_and_best_performing_strategy(self):
        """Verifies comparator computes HR, log-rank p-values, and qualifies best performing simulated strategy."""
        cohort = SyntheticCohortGenerator.generate_cohort(
            patient_data=self.patient_data,
            cohort_size=10,
            seed=99
        )

        scenario = CounterfactualScenario(
            scenario_id=f"scen-{cohort.cohort_id}",
            target_cohort=cohort,
            arms=["mtd", "adaptive", "combination"],
            duration=120,
            control_arm="mtd"
        )
        sim_output = CounterfactualSimulator.simulate_scenario(scenario)
        outcomes_by_arm = {
            arm_id: CounterfactualOutcomes.compute_arm_outcomes(arm_id, records, duration=120)
            for arm_id, records in sim_output["arm_results"].items()
        }

        comparison = CounterfactualComparator.compare_arms(
            sim_output,
            outcomes_by_arm,
            control_arm="mtd",
            anchor_patient_id=cohort.anchor_patient_id
        )

        self.assertIn("comparisons", comparison)
        self.assertIn("ranked_arms", comparison)
        # CRITICAL REFINEMENT 1: Must be best_performing_simulated_strategy (never unqualified optimal)
        self.assertIn("best_performing_simulated_strategy", comparison)
        best = comparison["best_performing_simulated_strategy"]
        self.assertIn("arm_id", best)
        self.assertIn("qualification", best)
        self.assertIn("simulated", best["qualification"].lower())
        self.assertIn("disclaimer", comparison)

    def test_counterfactual_registry_orchestration(self):
        """Tests full CounterfactualRegistry orchestration entrypoints and profiling."""
        # 1. Cohort generation endpoint
        cohort_res = CounterfactualRegistry.generate_synthetic_cohort(
            patient_data=self.patient_data,
            cohort_size=15,
            seed=77
        )
        self.assertIn("cohort", cohort_res)
        self.assertEqual(cohort_res["cohort"]["size"], 15)
        self.assertIn("processingTimeMs", cohort_res)

        # 2. Full comparative analysis pipeline
        full_res = CounterfactualRegistry.run_full_counterfactual_comparison({
            "patient": self.patient_data,
            "cohort_size": 10,
            "seed": 77,
            "arms": ["mtd", "adaptive", "metronomic"],
            "control_arm": "mtd",
            "duration": 90
        })

        self.assertIn("reproducibility_manifest", full_res)
        self.assertIn("cohort_summary", full_res)
        self.assertIn("treatment_arms", full_res)
        self.assertIn("outcomes_by_arm", full_res)
        self.assertIn("comparisons", full_res)
        self.assertIn("best_performing_simulated_strategy", full_res)
        self.assertIn("processingTimeMs", full_res)
        self.assertGreater(full_res["processingTimeMs"], 0.0)


if __name__ == '__main__':
    unittest.main()
