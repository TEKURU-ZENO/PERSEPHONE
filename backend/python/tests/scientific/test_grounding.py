# Test suite for Grounding / Hallucination Checker
import unittest
from backend.python.compute.plugins.graph_rag.grounding import validate_recommendation_grounding

class TestGroundingValidator(unittest.TestCase):
  def test_grounding_pass(self):
    graph_nodes = [{"id": "olaparib", "type": "Drug"}, {"id": "brca1-mut", "type": "Mutation"}]
    context = "Olaparib shows clinical benefit in BRCA1 mutations."
    
    result = validate_recommendation_grounding("olaparib", "brca1-mut", "Ovarian Cancer", context, graph_nodes)
    self.assertTrue(result["grounded"])
    self.assertEqual(result["score"], 1.0)
    self.assertEqual(len(result["violations"]), 0)

  def test_grounding_violation_missing_drug_in_literature(self):
    graph_nodes = [{"id": "olaparib", "type": "Drug"}, {"id": "brca1-mut", "type": "Mutation"}]
    context = "Standard chemotherapy regimens were evaluated."
    
    result = validate_recommendation_grounding("olaparib", "brca1-mut", "Ovarian Cancer", context, graph_nodes)
    self.assertFalse(result["grounded"])
    self.assertTrue(result["score"] < 1.0)
    self.assertTrue(any("does not exist in literature abstracts" in v for v in result["violations"]))

  def test_grounding_violation_missing_mutation_in_pathways(self):
    graph_nodes = [{"id": "olaparib", "type": "Drug"}] # brca1-mut missing
    context = "Olaparib shows clinical benefit in BRCA1 mutations."
    
    result = validate_recommendation_grounding("olaparib", "brca1-mut", "Ovarian Cancer", context, graph_nodes)
    self.assertFalse(result["grounded"])
    self.assertTrue(any("does not exist in Patient active pathways" in v for v in result["violations"]))

if __name__ == '__main__':
  unittest.main()
