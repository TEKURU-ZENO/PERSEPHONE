# Test suite for Cosine Similarity calculations
import unittest
from backend.python.compute.plugins.graph_rag.vector_search import calculate_cosine_similarity, search_literature

class TestCosineSimilarity(unittest.TestCase):
  def test_cosine_math(self):
    v1 = [1.0, 0.0, 0.0, 0.0]
    v2 = [1.0, 0.0, 0.0, 0.0]
    self.assertAlmostEqual(calculate_cosine_similarity(v1, v2), 1.0)

    v3 = [0.0, 1.0, 0.0, 0.0]
    self.assertAlmostEqual(calculate_cosine_similarity(v1, v3), 0.0)

    v4 = [1.0, 1.0, 0.0, 0.0]
    self.assertAlmostEqual(calculate_cosine_similarity(v1, v4), 0.70710678)

  def test_literature_search_sorting(self):
    results = search_literature("Evaluate targeted Olaparib therapy in BRCA1 mutations")
    self.assertTrue(len(results) > 0)
    
    # Highest similarity should be the Nature 2012 Olaparib paper
    self.assertEqual(results[0]["pmid"], "22960745")
    self.assertTrue(results[0]["cosineSimilarity"] > 0.8)

if __name__ == '__main__':
  unittest.main()
