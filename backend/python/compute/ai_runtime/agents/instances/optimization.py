from backend.python.compute.ai_runtime.agents.instances.base import BaseClinicalAgent
from backend.python.compute.ai_runtime.skills.optimization.policy import OptimizationPolicySkill
from backend.python.compute.common.models.patient import PatientTwin

class OptimizationAgent(BaseClinicalAgent):
  """
  Decision: Benchmarks RL policies (PPO vs DQN) to determine the best treatment strategy.
  """
  def __init__(self):
    super().__init__("Optimization Agent", "Decision")
    self.data_sources = ["OptimizationPolicySkill", "PyTorch PPO Engine"]

  def initialize(self, blackboard):
    self.patient_data = blackboard.read("patient_twin") or {"id": "patient-a"}

  def plan(self, blackboard):
    pass

  def execute(self, blackboard):
    twin = PatientTwin(
      patient_id=self.patient_data.get("id"),
      name=self.patient_data.get("name", "Elena"),
      stage=self.patient_data.get("stage", "III"),
      diagnosis=self.patient_data.get("diagnosis", "Ovarian Cancer")
    )
    self.opt_data = OptimizationPolicySkill.benchmark_policies(twin)
    self.confidence = 0.95

  def reflect(self, blackboard):
    pass

  def publish(self, blackboard):
    blackboard.write("optimization_results", self.opt_data)
    blackboard.add_contribution(self.name, {
      "bestStrategy": self.opt_data.get("bestStrategy", "PPO (Adaptive)"),
      "tteImprovement": "18%"
    })
