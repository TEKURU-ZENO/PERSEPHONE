"""
Counterfactual Registry module for PERSEPHONE Counterfactual Research Platform.
Provides unified orchestration, dispatch, and latency profiling for synthetic cohorts,
counterfactual trajectory simulations, comparative outcomes, and reproducibility manifests.
"""
import time
from backend.python.compute.counterfactual.cohort import SyntheticCohort
from backend.python.compute.counterfactual.generator import SyntheticCohortGenerator
from backend.python.compute.counterfactual.treatment_matrix import TreatmentMatrix
from backend.python.compute.counterfactual.scenario import CounterfactualScenario
from backend.python.compute.counterfactual.simulator import CounterfactualSimulator
from backend.python.compute.counterfactual.outcomes import CounterfactualOutcomes
from backend.python.compute.counterfactual.comparison import CounterfactualComparator
from backend.python.compute.counterfactual.provenance import CausalProvenanceEngine

class CounterfactualRegistry:
    """
    Public registry interface for PERSEPHONE Counterfactual Research Platform compute pipelines.
    """

    @classmethod
    def generate_synthetic_cohort(cls, patient_data=None, cohort_size=50, seed=42, variance_scale=0.15):
        start = time.perf_counter()
        cohort = SyntheticCohortGenerator.generate_cohort(
            patient_data=patient_data,
            cohort_size=cohort_size,
            seed=seed,
            variance_scale=variance_scale
        )
        elapsed = round((time.perf_counter() - start) * 1000, 2)
        return {
            "cohort": cohort.to_dict(),
            "processingTimeMs": elapsed
        }

    @classmethod
    def simulate_counterfactual_scenario(cls, payload=None):
        start = time.perf_counter()
        data = payload or {}
        patient_data = data.get("patient") or data.get("patient_data") or {"id": "patient-a"}
        cohort_size = int(data.get("cohort_size", 50))
        seed = int(data.get("seed", 42))
        arms = data.get("arms") or TreatmentMatrix.list_arm_ids()
        duration = int(data.get("duration", 180))

        cohort = SyntheticCohortGenerator.generate_cohort(
            patient_data=patient_data,
            cohort_size=cohort_size,
            seed=seed
        )

        scenario = CounterfactualScenario(
            scenario_id=f"scen-{cohort.cohort_id}",
            target_cohort=cohort,
            arms=arms,
            duration=duration,
            control_arm=data.get("control_arm", "mtd")
        )

        sim_output = CounterfactualSimulator.simulate_scenario(scenario)

        # Compute summary outcomes per arm
        outcomes_by_arm = {}
        for arm_id, sim_records in sim_output["arm_results"].items():
            outcomes_by_arm[arm_id] = CounterfactualOutcomes.compute_arm_outcomes(
                arm_id, sim_records, duration=duration
            )

        elapsed = round((time.perf_counter() - start) * 1000, 2)

        return {
            "scenario": scenario.to_dict(),
            "outcomes_by_arm": outcomes_by_arm,
            "processingTimeMs": elapsed
        }

    @classmethod
    def run_full_counterfactual_comparison(cls, payload=None):
        start = time.perf_counter()
        data = payload or {}
        patient_data = data.get("patient") or data.get("patient_data") or {"id": data.get("patientId", "patient-a")}
        cohort_size = int(data.get("cohort_size", 50))
        seed = int(data.get("seed", 42))
        arms = data.get("arms") or TreatmentMatrix.list_arm_ids()
        control_arm = data.get("control_arm", "mtd")
        duration = int(data.get("duration", 180))

        # 1. Synthetic Cohort
        cohort = SyntheticCohortGenerator.generate_cohort(
            patient_data=patient_data,
            cohort_size=cohort_size,
            seed=seed
        )

        # 2. Scenario
        scenario = CounterfactualScenario(
            scenario_id=f"scen-{cohort.cohort_id}",
            target_cohort=cohort,
            arms=arms,
            duration=duration,
            control_arm=control_arm
        )

        # 3. Simulate Multi-Arm Trajectories
        sim_output = CounterfactualSimulator.simulate_scenario(scenario)

        # 4. Endpoints & Outcomes
        outcomes_by_arm = {}
        for arm_id, sim_records in sim_output["arm_results"].items():
            outcomes_by_arm[arm_id] = CounterfactualOutcomes.compute_arm_outcomes(
                arm_id, sim_records, duration=duration
            )

        # 5. Comparative Analysis & Uncertainty
        comparison_res = CounterfactualComparator.compare_arms(
            sim_output,
            outcomes_by_arm,
            control_arm=control_arm,
            anchor_patient_id=cohort.anchor_patient_id
        )

        # 6. Reproducibility Manifest
        reproducibility = CausalProvenanceEngine.generate_reproducibility_manifest(
            anchor_patient_id=cohort.anchor_patient_id,
            cohort_seed=seed,
            simulation_seed=seed,
            arms=arms,
            biophysical_params=patient_data
        )

        elapsed = round((time.perf_counter() - start) * 1000, 2)

        return {
            "reproducibility_manifest": reproducibility,
            "cohort_summary": {
                "cohort_id": cohort.cohort_id,
                "cohort_size": cohort.size,
                "anchor_patient_id": cohort.anchor_patient_id,
                "distributions": cohort.get_distribution_summary()
            },
            "treatment_arms": TreatmentMatrix.get_all_regimens(),
            "outcomes_by_arm": outcomes_by_arm,
            "comparisons": comparison_res["comparisons"],
            "ranked_arms": comparison_res["ranked_arms"],
            "best_performing_simulated_strategy": comparison_res["best_performing_simulated_strategy"],
            "disclaimer": comparison_res["disclaimer"],
            "processingTimeMs": elapsed
        }
