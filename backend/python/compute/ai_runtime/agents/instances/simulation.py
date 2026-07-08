from backend.python.compute.ai_runtime.agents.instances.base import BaseClinicalAgent
from backend.python.compute.ai_runtime.skills.simulation.solver import SimulationSolverSkill
from backend.python.compute.common.models.patient import PatientTwin

class SimulationAgent(BaseClinicalAgent):
  """
  Simulation: Runs continuous mechanistic RK4 models.
  """
  def __init__(self):
    super().__init__("Simulation Agent", "Simulation")
    self.data_sources = ["SimulationSolverSkill", "RK4 Solver Engine"]

  def initialize(self, blackboard):
    self.patient_data = blackboard.read("patient_twin") or {"id": "patient-a"}

  def plan(self, blackboard):
    pass

  def execute(self, blackboard):
    # Convert patient dictionary to PatientTwin model if needed
    twin = PatientTwin(
      patient_id=self.patient_data.get("id"),
      name=self.patient_data.get("name", "Elena"),
      stage=self.patient_data.get("stage", "III"),
      diagnosis=self.patient_data.get("diagnosis", "Ovarian Cancer")
    )
    self.sim_data = SimulationSolverSkill.run_simulation(twin, "mtd")
    self.confidence = 0.98

  def reflect(self, blackboard):
    pass

  def publish(self, blackboard):
    blackboard.write("simulation_results", self.sim_data.to_json())
    blackboard.add_contribution(self.name, {
      "timeToProgressionDays": self.sim_data.time_to_progression,
      "maxToxicity": self.sim_data.max_toxicity
    })
