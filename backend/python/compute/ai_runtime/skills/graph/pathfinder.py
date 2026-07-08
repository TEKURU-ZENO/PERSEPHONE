from backend.python.compute.graph.pathfinding import find_causal_path

class GraphPathfinderSkill:
  """
  Skill executing graph path searches over entities and targets.
  """
  @staticmethod
  def find_path(patient_id, target_drug="Olaparib"):
    nodes, edges = find_causal_path(patient_id)
    return nodes
