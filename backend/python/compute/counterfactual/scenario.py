"""
Counterfactual Scenario configuration module for PERSEPHONE Counterfactual Research Platform.
Encapsulates scenario parameters, target synthetic cohort, and evaluation arms.
"""
from backend.python.compute.counterfactual.treatment_matrix import TreatmentMatrix

class CounterfactualScenario:
    """
    Defines a counterfactual simulation scenario comparing alternative treatment arms.
    """
    def __init__(self, scenario_id, target_cohort, arms=None, duration=180, step_size_h=0.5, control_arm="mtd", title=None):
        self.scenario_id = scenario_id
        self.target_cohort = target_cohort
        self.arms = arms or TreatmentMatrix.list_arm_ids()
        self.duration = int(duration)
        self.step_size_h = float(step_size_h)
        self.control_arm = control_arm if control_arm in self.arms else (self.arms[0] if self.arms else "mtd")
        self.title = title or f"Counterfactual Evaluation: {len(self.arms)} Arms on {target_cohort.cohort_id}"

    def to_dict(self):
        return {
            "scenario_id": self.scenario_id,
            "title": self.title,
            "cohort_id": self.target_cohort.cohort_id,
            "cohort_size": self.target_cohort.size,
            "arms": self.arms,
            "control_arm": self.control_arm,
            "duration_days": self.duration,
            "step_size_h": self.step_size_h
        }
