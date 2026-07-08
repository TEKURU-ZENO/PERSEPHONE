from backend.python.compute.ai_runtime.agents.instances.base import BaseClinicalAgent
from backend.python.compute.ai_runtime.skills.graph.pathfinder import GraphPathfinderSkill

class KnowledgeGraphAgent(BaseClinicalAgent):
  """
  Knowledge: Maps gene-to-drug pathway linkages.
  """
  def __init__(self):
    super().__init__("Knowledge Graph", "Knowledge")
    self.data_sources = ["GraphPathfinderSkill", "Biomedical KG Database"]

  def initialize(self, blackboard):
    self.patient_data = blackboard.read("patient_twin") or {"id": "patient-a"}

  def plan(self, blackboard):
    pass

  def execute(self, blackboard):
    self.paths = GraphPathfinderSkill.find_path(self.patient_data.get("id"), "Olaparib")
    self.confidence = 0.97

  def reflect(self, blackboard):
    pass

  def publish(self, blackboard):
    blackboard.write("kg_pathways", self.paths)
    blackboard.add_contribution(self.name, {
      "pathwaysResolved": len(self.paths),
      "targetGeneMatched": "BRCA1"
    })
