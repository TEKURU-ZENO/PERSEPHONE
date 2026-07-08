from backend.python.compute.ai_runtime.agents.instances.base import BaseClinicalAgent
from backend.python.compute.ai_runtime.cair import ClinicalAIRuntime

class ExplainabilityAgent(BaseClinicalAgent):
  """
  Governance: Generates clinician-friendly explanation trees.
  """
  def __init__(self):
    super().__init__("Explainability Agent", "Governance")
    self.data_sources = ["Causal Pathway Maps"]

  def initialize(self, blackboard):
    self.twin = blackboard.read("patient_twin") or {}
    self.paths = blackboard.read("kg_pathways") or []

  def plan(self, blackboard):
    pass

  def execute(self, blackboard):
    prompt = f"Create explainability rationale path choosing Olaparib for patient {self.twin.get('name', 'Elena')} with pathways {str(self.paths)}"
    res = ClinicalAIRuntime.generate_structured_response(
      prompt, 
      capability="json_mode", 
      system_instruction="You are the Explainability Agent."
    )
    self.rationale = res
    self.confidence = res.get("confidence", 0.94)

  def reflect(self, blackboard):
    pass

  def publish(self, blackboard):
    blackboard.write("explainability_rationale", self.rationale)
    blackboard.add_contribution(self.name, self.rationale)
