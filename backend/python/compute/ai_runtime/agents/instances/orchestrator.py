import json
from backend.python.compute.ai_runtime.agents.instances.base import BaseClinicalAgent
from backend.python.compute.ai_runtime.cair import ClinicalAIRuntime

class ChiefOrchestratorAgent(BaseClinicalAgent):
  """
  Chief Orchestrator Agent directing council workflow steps.
  """
  def __init__(self):
    super().__init__("Chief Orchestrator", "Coordination")
    self.data_sources = ["Blackboard State"]

  def initialize(self, blackboard):
    pass

  def plan(self, blackboard):
    pass

  def execute(self, blackboard):
    # Call CAIR to summarize task routing and DAG targets
    prompt = "Create task routing schedule for tumor board decision on BRCA1 ovarian cancer."
    res = ClinicalAIRuntime.generate_structured_response(
      prompt, 
      capability="json_mode", 
      system_instruction="You are the PERSEPHONE Chief Orchestrator."
    )
    self.confidence = res.get("confidence", 0.95)

  def reflect(self, blackboard):
    pass

  def publish(self, blackboard):
    blackboard.write("final_report", "Debate Orchestration Initialized.")
    blackboard.add_contribution(self.name, {"status": "orchestration_scheduled"})
