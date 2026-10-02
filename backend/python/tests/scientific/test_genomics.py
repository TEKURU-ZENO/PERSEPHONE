import unittest
from backend.python.compute.genomics.variant_annotator import VariantAnnotator
from backend.python.compute.genomics.pathway_enrichment import PathwayEnrichmentEngine
from backend.python.compute.genomics.biomarker_scorer import BiomarkerScorer
from backend.python.compute.genomics.signature_classifier import MutationSignatureClassifier
from backend.python.compute.genomics.registry import GenomicsRegistry

class TestVariantAnnotator(unittest.TestCase):
  def test_annotate_known_variant(self):
    result = VariantAnnotator.annotate_variant("BRCA1", "c.1961delA")
    self.assertEqual(result["gene"], "BRCA1")
    self.assertEqual(result["hgvsc"], "c.1961delA")
    self.assertEqual(result["clinical_significance"], "Pathogenic")
    self.assertIn("germline_assessment", result)
    self.assertIn("somatic_actionability", result)
    self.assertIsNotNone(result["germline_assessment"]["gnomad_af"])
    self.assertEqual(result["somatic_actionability"]["tier"], "Tier I-A")
    self.assertEqual(result["evidence_level"], "A")

  def test_mandatory_hgvsc(self):
    with self.assertRaises(TypeError):
      VariantAnnotator.annotate_variant("BRCA1")

  def test_somatic_vs_germline_distinction(self):
    tp53 = VariantAnnotator.annotate_variant("TP53", "c.524G>A")
    self.assertIn("Li-Fraumeni", tp53["germline_assessment"]["disease"])
    self.assertNotIn("Li-Fraumeni", tp53["somatic_actionability"]["disease"])
    self.assertIsNone(tp53["germline_assessment"]["gnomad_af"])

    kras_g12d = VariantAnnotator.annotate_variant("KRAS", "c.35G>A")
    self.assertIn("Tier III", kras_g12d["somatic_actionability"]["tier"])
    self.assertIsNone(kras_g12d["germline_assessment"]["gnomad_af"])

    kras_g12c = VariantAnnotator.annotate_variant("KRAS", "c.34G>T")
    self.assertEqual(kras_g12c["somatic_actionability"]["tier"], "Tier I-A")

  def test_annotate_unknown_variant(self):
    result = VariantAnnotator.annotate_variant("FAKEGENE", "c.999A>G")
    self.assertEqual(result["clinical_significance"], "VUS")

  def test_annotate_panel(self):
    panel = VariantAnnotator.annotate_panel([
      {"gene": "BRCA1", "hgvsc": "c.1961delA"},
      {"gene": "EGFR", "hgvsc": "c.2573T>G"},
      {"gene": "KRAS", "hgvsc": "c.35G>A"}
    ])
    self.assertEqual(len(panel), 3)
    self.assertEqual(panel[0]["gene"], "BRCA1")
    self.assertEqual(panel[1]["gene"], "EGFR")

  def test_classify_pathogenicity(self):
    variant = VariantAnnotator.annotate_variant("BRCA1", "c.1961delA")
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
    variant = VariantAnnotator.annotate_variant("BRCA1", "c.1961delA")
    result = BiomarkerScorer.score_actionability(variant)
    self.assertIn("actionability_tier", result)
    self.assertIn("evidence_level", result)
    self.assertIn("therapeutic_implications", result)
    self.assertTrue(result["actionability_tier"].startswith("Tier"))

  def test_rank_biomarkers(self):
    panel = VariantAnnotator.annotate_panel([
      {"gene": "BRCA1", "hgvsc": "c.1961delA"},
      {"gene": "EGFR", "hgvsc": "c.2573T>G"},
      {"gene": "TP53", "hgvsc": "c.524G>A"}
    ])
    ranked = BiomarkerScorer.rank_biomarkers(panel)
    self.assertEqual(len(ranked), 3)
    # Tier I should be ranked before Tier II+
    self.assertTrue(ranked[0]["actionability_tier"].startswith("Tier I"))

class TestSignatureClassifier(unittest.TestCase):
  def test_classify_hrd_signature(self):
    counts = MutationSignatureClassifier.generate_synthetic_counts(["BRCA1"], total_mutations=200)
    result = MutationSignatureClassifier.classify_signature(counts)
    self.assertIn("dominant_signature", result)
    self.assertEqual(result["dominant_signature"], "SBS3")
    self.assertIn("cosine_similarity", result)
    self.assertGreater(result["cosine_similarity"], 0.85)
    self.assertIn("confidence", result)
    self.assertGreater(result["confidence"], 0.85)

  def test_classify_invalid_length(self):
    with self.assertRaises(ValueError):
      MutationSignatureClassifier.classify_signature([1.0] * 50)

  def test_classify_underpowered_warning(self):
    counts = [0.0] * 96
    counts[0] = 10.0
    result = MutationSignatureClassifier.classify_signature(counts)
    self.assertIsNotNone(result["warning"])
    self.assertIn("< 50", result["warning"])

  def test_compute_tmb(self):
    res_low = MutationSignatureClassifier.compute_tmb(297, exome_size_mb=30.0)
    self.assertAlmostEqual(res_low["tmb_score"], 9.9, places=1)
    self.assertEqual(res_low["tmb_status"], "TMB-Low")

    res_high = MutationSignatureClassifier.compute_tmb(300, exome_size_mb=30.0)
    self.assertAlmostEqual(res_high["tmb_score"], 10.0, places=1)
    self.assertEqual(res_high["tmb_status"], "TMB-High")

  def test_compute_msi(self):
    # Bethesda 5-marker panel tests
    loci_mss = [{"locus": f"L{i}", "stable": True} for i in range(5)]
    self.assertEqual(MutationSignatureClassifier.compute_msi_score(loci_mss)["msi_status"], "MSS")

    loci_msil = [{"locus": "L0", "stable": False}] + [{"locus": f"L{i}", "stable": True} for i in range(1, 5)]
    self.assertEqual(MutationSignatureClassifier.compute_msi_score(loci_msil)["msi_status"], "MSI-L")

    loci_msih = [{"locus": f"L{i}", "stable": False} for i in range(2)] + [{"locus": f"L{i}", "stable": True} for i in range(2, 5)]
    self.assertEqual(MutationSignatureClassifier.compute_msi_score(loci_msih)["msi_status"], "MSI-H")

    # Non-standard panel tests
    loci_non_mss = [{"locus": f"L{i}", "stable": False} for i in range(2)] + [{"locus": f"L{i}", "stable": True} for i in range(2, 10)]
    self.assertEqual(MutationSignatureClassifier.compute_msi_score(loci_non_mss)["msi_status"], "MSS")

    loci_non_msih = [{"locus": f"L{i}", "stable": False} for i in range(4)] + [{"locus": f"L{i}", "stable": True} for i in range(4, 10)]
    self.assertEqual(MutationSignatureClassifier.compute_msi_score(loci_non_msih)["msi_status"], "MSI-H")

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
