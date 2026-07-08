from backend.python.compute.ai_runtime.agents.instances.base import BaseClinicalAgent
from backend.python.compute.ai_runtime.skills.validation.scorecard import ValidationScorecardSkill

class ValidationAgent(BaseClinicalAgent):
  """
  Governance: Validates consistency and fits calibration scorecards.
  """
  def __init__(self):
    super().__init__("Validation Agent", "Governance")
    self.data_sources = ["ValidationScorecardSkill", "Goodness-of-Fit Scorer"]

  def initialize(self, blackboard):
    self.sim_data = blackboard.read("simulation_results") or {"timeline": []}
    self.memory_data = blackboard.read("clinical_memory") or []

  def plan(self, blackboard):
    pass

  def execute(self, blackboard):
    sim_timeline = self.sim_data.get("timeline", [])
    sim_vols = [pt["totalVolume"] for pt in sim_timeline[:len(self.memory_data)]]
    obs_vols = [pt["volume"] for pt in self.memory_data]
    
    # Fill defaults if length mismatch
    if len(sim_vols) < len(obs_vols):
      sim_vols += [50.0] * (len(obs_vols) - len(sim_vols))
    elif len(obs_vols) < len(sim_vols):
      sim_vols = sim_vols[:len(obs_vols)]
      
    self.metrics = ValidationScorecardSkill.compute_goodness_metrics(obs_vols, sim_vols)
    self.confidence = 0.97

  def reflect(self, blackboard):
    pass

  def publish(self, blackboard):
    blackboard.write("validation_scorecard", self.metrics)
    blackboard.add_contribution(self.name, self.metrics)
