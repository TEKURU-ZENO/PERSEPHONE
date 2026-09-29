"""
Counterfactual Reasoning Agent: 21st Council Member for PERSEPHONE.
Executes multi-arm counterfactual simulations over synthetic digital twin cohorts,
quantifies causal treatment effects (ATE, Hazard Ratios with 95% CIs),
and identifies the best-performing simulated strategy under mechanistic assumptions.
"""
from backend.python.compute.ai_runtime.agents.instances.base import BaseClinicalAgent
from backend.python.compute.counterfactual.registry import CounterfactualRegistry

class CounterfactualReasoningAgent(BaseClinicalAgent):
    """
    Counterfactual Reasoning Agent:
    Simulates alternative therapeutic regimens across synthetic digital twin cohorts
    anchored to the patient twin, calculating comparative survival and toxicity endpoints.

    Council classification: Scientific / Simulation
    """
    def __init__(self):
        super().__init__("Counterfactual Reasoning Agent", "Scientific")
        self.data_sources = [
            "CounterfactualRegistry",
            "SyntheticCohortGenerator",
            "CounterfactualSimulator",
            "CounterfactualComparator",
            "CounterfactualUncertaintyEngine"
        ]

    def initialize(self, blackboard):
        self.patient_data = blackboard.read("patient_twin") or {}
        self.response_intel = blackboard.read("RESPONSE_INTELLIGENCE") or {}
        self.sim_res = blackboard.read("simulation_results") or {}
        self.top_trial = blackboard.read("TOP_TRIAL") or {}
        self.cf_results = None

    def plan(self, blackboard):
        """
        Builds scenario execution payload for multi-arm synthetic cohort counterfactual simulation.
        """
        patient_id = self.patient_data.get("id") or "patient-a"
        variants = self.patient_data.get("variants") or ["BRCA1"]

        self.payload = {
            "patientId": patient_id,
            "patient": {
                "id": patient_id,
                "variants": variants,
                "tumor_volume": self.patient_data.get("tumor_volume", 82.0)
            },
            "cohort_size": 50,
            "seed": 42,
            "control_arm": "mtd",
            "duration": 180
        }

    def execute(self, blackboard):
        self.cf_results = CounterfactualRegistry.run_full_counterfactual_comparison(self.payload)
        self.confidence = 0.94

    def reflect(self, blackboard):
        """
        Evaluates simulation robustness and flags if all arms fail to surpass baseline MTD.
        """
        if self.cf_results:
            best_strat = self.cf_results.get("best_performing_simulated_strategy", {})
            arm_id = best_strat.get("arm_id", "mtd")
            utility = best_strat.get("utility_score", 0.0)
            if utility < 0.10:
                self.errors = f"CAUTION: Limited comparative divergence across counterfactual arms (utility: {utility:.2f})."

    def publish(self, blackboard):
        res = self.cf_results or {}
        best_strat = res.get("best_performing_simulated_strategy", {})
        comparisons = res.get("comparisons", {})
        reproducibility = res.get("reproducibility_manifest", {})

        # Isolated Blackboard publications
        blackboard.write("COUNTERFACTUAL_EXPERIMENT", res)
        blackboard.write("BEST_PERFORMING_SIMULATED_STRATEGY", best_strat)
        blackboard.write("COUNTERFACTUAL_COMPARISON", comparisons)
        blackboard.write("SYNTHETIC_COHORT_SUMMARY", res.get("cohort_summary", {}))
        blackboard.write("REPRODUCIBILITY_MANIFEST", reproducibility)

        top_arm = best_strat.get("arm_id", "adaptive")
        comp_top = comparisons.get(top_arm, {})
        ate_val = comp_top.get("average_treatment_effect", {}).get("value", 0.0)
        hr_val = comp_top.get("hazard_ratio", {}).get("value", 1.0)

        blackboard.add_contribution(self.name, {
            "best_performing_simulated_strategy": top_arm,
            "simulated_ate_ttp_days": ate_val,
            "simulated_hazard_ratio": hr_val,
            "synthetic_cohort_size": res.get("cohort_summary", {}).get("cohort_size", 50),
            "reproducibility_id": reproducibility.get("experiment_id", "exp-cf-001"),
            "qualification": "Research simulation projection; not a clinical directive"
        })
