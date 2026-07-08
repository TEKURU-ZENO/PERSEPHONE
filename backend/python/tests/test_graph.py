import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from backend.python.compute.graph.pathfinding import find_causal_path

class TestGraph(unittest.TestCase):
  def test_patient_a_pathway(self):
    nodes, edges = find_causal_path("patient-a")
    
    # Should include patient, brca1 mutation, and olaparib drug
    node_types = [n["type"] for n in nodes]
    node_ids = [n["id"] for n in nodes]

    self.assertIn("Patient", node_types)
    self.assertIn("Mutation", node_types)
    self.assertIn("Drug", node_types)
    self.assertIn("patient-a", node_ids)
    self.assertIn("brca1-mut", node_ids)
    self.assertIn("olaparib", node_ids)

if __name__ == '__main__':
  unittest.main()
