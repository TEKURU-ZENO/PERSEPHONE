import unittest
from backend.python.compute.pharmacogenomics.drug_gene_resolver import DrugGeneResolver
from backend.python.compute.pharmacogenomics.sensitivity_predictor import SensitivityPredictor
from backend.python.compute.pharmacogenomics.resistance_mapper import ResistanceMapper
from backend.python.compute.pharmacogenomics.synergy_estimator import SynergyEstimator
from backend.python.compute.pharmacogenomics.registry import PharmacogenomicsRegistry

class TestDrugGeneResolver(unittest.TestCase):
  def test_resolve_interactions_known_gene(self):
    result = DrugGeneResolver.resolve_interactions("BRCA1")
    self.assertIsInstance(result, list)
    self.assertGreater(len(result), 0)
    self.assertIn("drug", result[0])
    self.assertIn("interaction_type", result[0])

  def test_resolve_interactions_unknown_gene(self):
    result = DrugGeneResolver.resolve_interactions("FAKEGENE")
    self.assertIsInstance(result, list)
    self.assertEqual(len(result), 0)

  def test_get_contraindications(self):
    result = DrugGeneResolver.get_contraindications(["EGFR", "KRAS"])
    self.assertIsInstance(result, list)
    # EGFR and KRAS both have contraindications
    self.assertGreater(len(result), 0)

class TestSensitivityPredictor(unittest.TestCase):
  def test_predict_sensitivity(self):
    result = SensitivityPredictor.predict_sensitivity(
      ["BRCA1"], ["Olaparib", "Osimertinib"]
    )
    self.assertIsInstance(result, list)
    self.assertGreater(len(result), 0)
    self.assertIn("predicted_ic50", result[0])
    self.assertIn("sensitivity_class", result[0])

  def test_rank_drugs(self):
    preds = SensitivityPredictor.predict_sensitivity(
      ["EGFR"], ["Osimertinib", "Erlotinib"]
    )
    ranked = SensitivityPredictor.rank_drugs(preds)
    self.assertIsInstance(ranked, list)
    # Should be sorted by IC50 ascending
    if len(ranked) >= 2:
      self.assertLessEqual(ranked[0]["predicted_ic50"], ranked[-1]["predicted_ic50"])

class TestResistanceMapper(unittest.TestCase):
  def test_map_resistance_mechanisms(self):
    result = ResistanceMapper.map_resistance_mechanisms(["EGFR"])
    self.assertIsInstance(result, list)
    self.assertGreater(len(result), 0)
    self.assertIn("mechanism", result[0])
    self.assertIn("resistance_type", result[0])
    self.assertIn("alternative_drugs", result[0])

  def test_predict_resistance_timeline(self):
    result = ResistanceMapper.predict_resistance_timeline({"resistance_type": "acquired"})
    self.assertIn("estimated_months_to_resistance", result)
    self.assertGreater(result["estimated_months_to_resistance"], 0)

class TestSynergyEstimator(unittest.TestCase):
  def test_estimate_known_synergy(self):
    result = SynergyEstimator.estimate_synergy("Dabrafenib", "Trametinib")
    self.assertIn("synergy_score", result)
    self.assertGreater(result["synergy_score"], 0)
    self.assertEqual(result["interaction_type"], "synergistic")

  def test_estimate_unknown_synergy(self):
    result = SynergyEstimator.estimate_synergy("DrugA", "DrugB")
    self.assertIn("synergy_score", result)
    self.assertAlmostEqual(result["synergy_score"], 0.0, places=1)

  def test_rank_combinations(self):
    result = SynergyEstimator.rank_combinations(["Dabrafenib", "Trametinib", "Vemurafenib"])
    self.assertIsInstance(result, list)
    self.assertGreater(len(result), 0)

class TestPharmacogenomicsRegistry(unittest.TestCase):
  def test_run_pipeline(self):
    result = PharmacogenomicsRegistry.run_pharmacogenomics_pipeline(
      gene_variants=["BRCA1", "EGFR"]
    )
    self.assertIn("interactions", result)
    self.assertIn("sensitivity_predictions", result)
    self.assertIn("ranked_drugs", result)
    self.assertIn("resistance_mechanisms", result)
    self.assertIn("contraindications", result)
    self.assertIn("synergy_matrix", result)
    self.assertIn("processing_time_ms", result)
    self.assertGreater(len(result["interactions"]), 0)
    self.assertGreater(len(result["ranked_drugs"]), 0)

if __name__ == '__main__':
  unittest.main()
