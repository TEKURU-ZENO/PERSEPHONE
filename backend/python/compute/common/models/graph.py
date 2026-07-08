class KnowledgeGraphPath:
  def __init__(self, nodes, edges):
    self.nodes = nodes
    self.edges = edges

  def to_json(self):
    return {
      "nodes": self.nodes,
      "edges": self.edges
    }
