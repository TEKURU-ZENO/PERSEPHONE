from backend.python.compute.ai_runtime.agents.instances.base import BaseClinicalAgent
from backend.python.compute.ai_runtime.cair import ClinicalAIRuntime

class EvidenceAgent(BaseClinicalAgent):
  """
  Knowledge: Evidence Agent summarizing PubMed and NCCN guides.
  """
  def __init__(self):
    super().__init__("Evidence Agent", "Knowledge")
    self.data_sources = ["PubMed Literature", "NCCN Guidelines"]

  def initialize(self, blackboard):
    pass

  def plan(self, blackboard):
    pass

  def execute(self, blackboard):
    prompt = "Summarize clinical trials for Olaparib choice in ovarian cancer."
    res = ClinicalAIRuntime.generate_structured_response(
      prompt, 
      capability="json_mode", 
      system_instruction="You are the Evidence Agent."
    )
    self.evidence = res
    self.confidence = res.get("confidence", 0.91)

  def reflect(self, blackboard):
    pass

  def publish(self, blackboard):
    blackboard.write("literature_evidence", self.evidence)
    blackboard.add_contribution(self.name, self.evidence)
