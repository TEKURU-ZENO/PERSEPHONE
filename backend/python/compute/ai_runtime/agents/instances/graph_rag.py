from backend.python.compute.ai_runtime.agents.instances.base import BaseClinicalAgent
from backend.python.compute.ai_runtime.cair import ClinicalAIRuntime

class GraphRAGAgent(BaseClinicalAgent):
  """
  Knowledge: Compiles grounded evidence packs.
  """
  def __init__(self):
    super().__init__("Graph-RAG Agent", "Knowledge")
    self.data_sources = ["Biomedical KG", "Literature Embeddings"]

  def initialize(self, blackboard):
    self.paths = blackboard.read("kg_pathways") or []

  def plan(self, blackboard):
    pass

  def execute(self, blackboard):
    prompt = f"Ground evidence choosing Olaparib for ovarian cancer BRCA1 with pathway links: {str(self.paths)}"
    res = ClinicalAIRuntime.generate_structured_response(
      prompt, 
      capability="json_mode", 
      system_instruction="You are the Graph-RAG Agent."
    )
    self.pack = res
    self.confidence = res.get("confidence", 0.93)

  def reflect(self, blackboard):
    pass

  def publish(self, blackboard):
    blackboard.write("grounded_evidence", self.pack)
    blackboard.add_contribution(self.name, self.pack)
