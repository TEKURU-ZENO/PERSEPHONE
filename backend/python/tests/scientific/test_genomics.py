import unittest
from backend.python.compute.genomics.variant_annotator import VariantAnnotator
from backend.python.compute.genomics.pathway_enrichment import PathwayEnrichmentEngine
from backend.python.compute.genomics.biomarker_scorer import BiomarkerScorer
from backend.python.compute.genomics.signature_classifier import MutationSignatureClassifier
from backend.python.compute.genomics.registry import GenomicsRegistry

class TestVariantAnnotator(unittest.TestCase):
  def test_annotate_known_variant(self):
    result = VariantAnnotator.annotate_variant("BRCA1")
    self.assertEqual(result["gene"], "BRCA1")
    self.assertEqual(result["clinical_significance"], "Pathogenic")
    self.assertIn("allele_frequency", result)
    self.assertIn("evidence_level", result)

  def test_annotate_unknown_variant(self):
    result = VariantAnnotator.annotate_variant("FAKEGENE")
    self.assertEqual(result["clinical_significance"], "VUS")

  def test_annotate_panel(self):
    panel = VariantAnnotator.annotate_panel(["BRCA1", "EGFR", "KRAS"])
    self.assertEqual(len(panel), 3)
    self.assertEqual(panel[0]["gene"], "BRCA1")
    self.assertEqual(panel[1]["gene"], "EGFR")

  def test_classify_pathogenicity(self):
    variant = VariantAnnotator.annotate_variant("BRCA1")
    classification = VariantAnnotator.classify_pathogenicity(variant)
    self.assertEqual(classification, "Pathogenic")

class TestPathwayEnrichment(unittest.TestCase):
  def test_enrich_variants(self):
    result = PathwayEnrichmentEngine.enrich_variants(["BRCA1", "KRAS"])
    self.assertIn("enriched_pathways", result)
    pathways = result["enriched_pathways"]
    self.assertGreater(len(pathways), 0)
    self.assertIn("pathway_name", pathways[0])
    self.assertIn("p_value", pathways[0])
    self.assertIn("fold_enrichment", pathways[0])

  def test_compute_pathway_impact_score(self):
    result = PathwayEnrichmentEngine.enrich_variants(["BRCA1"])
    pathways = result.get("enriched_pathways", [])
    score = PathwayEnrichmentEngine.compute_pathway_impact_score(pathways)
    self.assertIsInstance(score, float)
    self.assertGreaterEqual(score, 0.0)
    self.assertLessEqual(score, 1.0)

class TestBiomarkerScorer(unittest.TestCase):
  def test_score_actionability(self):
    variant = VariantAnnotator.annotate_variant("BRCA1")
    result = BiomarkerScorer.score_actionability(variant)
    self.assertIn("actionability_tier", result)
    self.assertIn("evidence_level", result)
    self.assertIn("therapeutic_implications", result)
    self.assertTrue(result["actionability_tier"].startswith("Tier"))

  def test_rank_biomarkers(self):
    panel = VariantAnnotator.annotate_panel(["BRCA1", "EGFR", "TP53"])
    ranked = BiomarkerScorer.rank_biomarkers(panel)
    self.assertEqual(len(ranked), 3)
    # Tier I should be ranked before Tier II+
    self.assertTrue(ranked[0]["actionability_tier"].startswith("Tier I"))

class TestSignatureClassifier(unittest.TestCase):
  def test_classify_hrd_signature(self):
    result = MutationSignatureClassifier.classify_signature({"genes": ["BRCA1"]})
    self.assertIn("dominant_signature", result)
    self.assertIn("HRD", result["dominant_signature"])
    self.assertIn("confidence", result)

  def test_compute_tmb(self):
    result = MutationSignatureClassifier.compute_tmb(300, exome_size_mb=30.0)
    self.assertIn("tmb_score", result)
    self.assertAlmostEqual(result["tmb_score"], 10.0, places=1)
    self.assertIn("tmb_status", result)

  def test_compute_msi(self):
    loci = [
      {"locus": "BAT25", "stable": True},
      {"locus": "BAT26", "stable": True},
      {"locus": "NR21", "stable": False},
      {"locus": "NR24", "stable": True},
      {"locus": "MONO27", "stable": True}
    ]
    result = MutationSignatureClassifier.compute_msi_score(loci)
    self.assertIn("msi_score", result)
    self.assertIn("msi_status", result)
    self.assertEqual(result["msi_status"], "MSS")  # 1/5 = 0.2 < 0.3

class TestGenomicsRegistry(unittest.TestCase):
  def test_run_genomic_pipeline(self):
    result = GenomicsRegistry.run_genomic_pipeline({
      "genes": ["BRCA1", "EGFR", "KRAS"],
      "variant_count": 24,
      "microsatellite_loci": [
        {"locus": "BAT25", "stable": True},
        {"locus": "NR21", "stable": False}
      ]
    })
    self.assertIn("annotated_variants", result)
    self.assertIn("pathway_enrichment", result)
    self.assertIn("ranked_biomarkers", result)
    self.assertIn("mutation_signature", result)
    self.assertIn("tmb", result)
    self.assertIn("msi", result)
    self.assertIn("pathway_impact_score", result)
    self.assertIn("processing_time_ms", result)
    self.assertEqual(len(result["annotated_variants"]), 3)

if __name__ == '__main__':
  unittest.main()
