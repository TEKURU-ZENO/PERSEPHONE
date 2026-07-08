from backend.python.compute.ai_runtime.agents.instances.base import BaseClinicalAgent
from backend.python.compute.ai_runtime.cair import ClinicalAIRuntime

class ClinicalReportAgent(BaseClinicalAgent):
  """
  Governance: Formats the final Tumor Board decision report.
  """
  def __init__(self):
    super().__init__("Clinical Report", "Governance")
    self.data_sources = ["Blackboard Contributions"]

  def initialize(self, blackboard):
    self.contribs = blackboard.read("agent_contributions") or []

  def plan(self, blackboard):
    pass

  def execute(self, blackboard):
    prompt = f"Summarize final Tumor Board Report based on agent contributions: {str(self.contribs)}"
    res = ClinicalAIRuntime.generate_structured_response(
      prompt, 
      capability="json_mode", 
      system_instruction="You are the Clinical Report Agent."
    )
    self.report = res
    self.confidence = res.get("confidence", 0.95)

  def reflect(self, blackboard):
    pass

  def publish(self, blackboard):
    blackboard.write("final_report", self.report)
    blackboard.add_contribution(self.name, self.report)
