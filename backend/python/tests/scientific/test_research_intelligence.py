import unittest
from backend.python.compute.research_intelligence.graph.evidence_graph import (
  ClinicalEvidenceGraph, EvidenceNode, EvidenceEdge
)
from backend.python.compute.research_intelligence.graph.traverser import EvidenceGraphTraverser
from backend.python.compute.research_intelligence.literature.citation import CitationManager
from backend.python.compute.research_intelligence.literature.evidence import EvidenceExtractor
from backend.python.compute.research_intelligence.literature.retrieval import LiteratureRetriever
from backend.python.compute.research_intelligence.guidelines.schemas import GuidelineReference, DecisionRule
from backend.python.compute.research_intelligence.guidelines.temporal import TemporalValidityEngine
from backend.python.compute.research_intelligence.guidelines.parser import GuidelineParser
from backend.python.compute.research_intelligence.guidelines.recommendation import GuidelineRecommender
from backend.python.compute.research_intelligence.trials.evidence_linker import TrialEvidenceLinker
from backend.python.compute.research_intelligence.knowledge.hypothesis import ClinicalHypothesisGenerator
from backend.python.compute.research_intelligence.knowledge.contradiction import ContradictionDetector
from backend.python.compute.research_intelligence.provenance.source import ProvenanceSource
from backend.python.compute.research_intelligence.provenance.evidence_item import EvidenceItem
from backend.python.compute.research_intelligence.provenance.claim import ClinicalClaim
from backend.python.compute.research_intelligence.provenance.verifier import EvidenceVerifier
from backend.python.compute.research_intelligence.provenance.grounding import GroundingGate
from backend.python.compute.research_intelligence.provenance.lineage import EvidenceLineageTracker
from backend.python.compute.research_intelligence.registry import ResearchIntelligenceRegistry


class TestResearchIntelligence(unittest.TestCase):

  def setUp(self):
    self.patient = {
      "id": "patient-a",
      "name": "Elena Rostova",
      "disease": "OVARIAN",
      "tumorType": "High-Grade Serous Ovarian Cancer",
      "stage": "Stage IIIc",
      "variants": ["BRCA1 185delAG"],
      "hrd_score": 62.0
    }

  def test_evidence_graph_assembly_and_traversal(self):
    graph = ClinicalEvidenceGraph()
    graph.add_node("pat_1", "PATIENT", "Elena Rostova")
    graph.add_node("var_1", "VARIANT", "BRCA1 185delAG")
    graph.add_node("drg_1", "DRUG", "Olaparib")
    graph.add_node("pub_1", "PUBLICATION", "NEJM 2018 (SOLO-1)")
    graph.add_node("clm_1", "CLAIM", "Synthetic Lethality Sensitivity")

    graph.add_edge("pat_1", "var_1", "HAS_VARIANT")
    graph.add_edge("clm_1", "pub_1", "SUPPORTED_BY")
    graph.add_edge("clm_1", "drg_1", "TARGETS")

    self.assertEqual(len(graph.nodes), 5)
    self.assertEqual(len(graph.edges), 3)

    ancestry = EvidenceGraphTraverser.trace_claim_lineage(graph, "clm_1")
    node_ids = [n["id"] for n in ancestry["nodes"]]
    self.assertIn("clm_1", node_ids)

  def test_citation_manager_formatting(self):
    paper = {
      "authors": ["Moore K", "Colombo N", "Scambia G"],
      "title": "Maintenance Olaparib in Patients with Newly Diagnosed Advanced Ovarian Cancer",
      "journal": "N Engl J Med",
      "year": 2018,
      "volume": "379",
      "issue": "26",
      "pages": "2495-2505",
      "pmid": "30345884",
      "doi": "10.1056/NEJMoa1810858",
      "nct_id": "NCT01844986"
    }
    citation = CitationManager.format_vancouver(paper)
    self.assertIn("Moore K", citation)
    self.assertIn("N Engl J Med", citation)

    resolved = CitationManager.resolve_identifiers(paper)
    urls = resolved.get("urls", {})
    self.assertIn("pubmed_url", urls)
    self.assertIn("doi_url", urls)
    self.assertIn("clinical_trials_url", urls)

  def test_orthogonal_evidence_grading(self):
    paper = {
      "pmid": "30345884",
      "phase": "Phase III",
      "hazard_ratio": 0.30,
      "hr_ci_lower": 0.23,
      "hr_ci_upper": 0.41,
      "median_pfs_delta_months": 13.8,
      "sample_size": 391,
      "cebm_level": "Level 1b",
      "grade_rating": "High"
    }
    extracted = EvidenceExtractor.extract_evidence(paper)
    quality = extracted["quality_grading"]

    # Verify that CEBM and GRADE ratings remain orthogonal and are never collapsed
    self.assertEqual(quality["cebm_level"], "Level 1b")
    self.assertEqual(quality["grade_rating"], "High")
    self.assertNotEqual(quality["cebm_level"], quality["grade_rating"])
    self.assertAlmostEqual(extracted["hazard_ratio"]["value"], 0.30)
    self.assertTrue(extracted["hazard_ratio"]["statistically_significant"])

  def test_curated_literature_retrieval(self):
    results = LiteratureRetriever.query({"query": "BRCA1 Olaparib maintenance ovarian", "limit": 5})
    self.assertGreater(len(results), 0)
    top_hit = results[0]
    self.assertTrue("SOLO-1" in top_hit.get("title", "") or "SOLO-1" in top_hit.get("abstract", "") or "Olaparib" in top_hit.get("title", ""))

  def test_temporal_validity_engine(self):
    res_curr = TemporalValidityEngine.evaluate_temporal_validity(
      effective_from="2024-01-01",
      effective_until="2027-12-31",
      superseded_by=None
    )
    self.assertEqual(res_curr["validity_status"], "CURRENT")
    self.assertTrue(res_curr["is_actionable"])

    res_super = TemporalValidityEngine.evaluate_temporal_validity(
      effective_from="2020-01-01",
      effective_until="2023-12-31",
      superseded_by="NCCN-OV-v1.2026"
    )
    self.assertEqual(res_super["validity_status"], "SUPERSEDED")
    self.assertFalse(res_super["is_actionable"])

  def test_guideline_evaluation(self):
    matches = GuidelineRecommender.evaluate_patient_guidelines(self.patient, proposed_drug="Olaparib")
    self.assertGreater(len(matches), 0)
    nccn_match = next((m for m in matches if m["organization"] == "NCCN"), None)
    self.assertIsNotNone(nccn_match)
    self.assertIn("Category 1", nccn_match["evidence_category"])
    self.assertEqual(nccn_match["temporal_validity"]["validity_status"], "CURRENT")

  def test_trial_evidence_linker(self):
    chain = TrialEvidenceLinker.build_trial_evidence_chain("NCT01844986")
    self.assertEqual(chain["trial_name"], "SOLO-1")
    self.assertEqual(chain["primary_pmid"], "30345884")
    self.assertEqual(chain["drug"], "Olaparib")
    self.assertEqual(chain["link_status"], "VERIFIED")

  def test_contradiction_detection_categories(self):
    # Test population and biomarker contradiction detection
    patient_negative = {
      "id": "patient-neg",
      "disease": "OVARIAN",
      "variants": [],
      "hrd_score": 15.0
    }
    result = ContradictionDetector.scan_contradictions(
      patient_data=patient_negative,
      proposed_drug="Olaparib",
      retrieved_papers=[],
      guideline_recommendations=[]
    )
    categories = [c["category"] for c in result["conflicts"]]
    self.assertIn("BIOMARKER_CONFLICT", categories)

  def test_cryptographic_lineage_and_merkle_root(self):
    src = ProvenanceSource(
      source_id="src_1",
      source_type="PUBMED",
      uri="https://doi.org/10.1056/NEJMoa1810858",
      version="2018",
      title="NEJM SOLO-1 Article",
      raw_content="SOLO-1 Olaparib maintenance"
    )
    self.assertTrue(len(src.content_hash) == 64)

    item = EvidenceItem(
      evidence_id="ev_1",
      source_id="src_1",
      source_hash=src.content_hash,
      study_design="Phase III Randomized Controlled Trial",
      sample_size=391,
      hazard_ratio={"value": 0.30, "lower": 0.23, "upper": 0.41},
      median_pfs_delta_months=13.8,
      cebm_level="Level 1b",
      grade_rating="High",
      nccn_category="Category 1"
    )
    self.assertTrue(len(item.evidence_hash) == 64)

    claim = ClinicalClaim(
      claim_id="clm_1",
      patient_id="patient-a",
      statement="BRCA1 deficiency induces PARP inhibitor sensitivity",
      evidence_ids=["ev_1"],
      source_ids=["src_1"],
      generating_agent="research_intelligence"
    )
    self.assertTrue(len(claim.provenance_hash) == 64)

    lineage = EvidenceLineageTracker.build_claim_lineage(claim, [item], [src])
    self.assertIn("lineage_root_hash", lineage)
    self.assertEqual(len(lineage["lineage_root_hash"]), 64)

  def test_grounding_gate_enforcement(self):
    src = ProvenanceSource("src_1", "PUBMED", "https://pubmed.ncbi.nlm.nih.gov/30345884", "2018", "SOLO-1")
    item = EvidenceItem(
      "ev_1", "src_1", src.content_hash, "RCT", 391,
      {"value": 0.30}, 13.8, "Level 1b", "High", "Category 1"
    )

    # Claim with strong evidence -> VERIFIED
    claim_good = ClinicalClaim(
      claim_id="clm_good",
      patient_id="patient-a",
      statement="PARP inhibition is effective in BRCA1-mutated tumors",
      evidence_ids=["ev_1"],
      source_ids=["src_1"],
      generating_agent="research_intelligence"
    )
    res_good = GroundingGate.evaluate_claim(claim_good, available_evidence=[item])
    self.assertEqual(res_good["grounding_status"], "VERIFIED")
    self.assertTrue(res_good["allow_clinical_presentation"])

    # Claim with no evidence -> UNGROUNDED (blocked)
    claim_bad = ClinicalClaim(
      claim_id="clm_bad",
      patient_id="patient-a",
      statement="Ungrounded assertion with zero evidence",
      evidence_ids=[],
      source_ids=[],
      generating_agent="research_intelligence"
    )
    res_bad = GroundingGate.evaluate_claim(claim_bad, available_evidence=[item])
    self.assertEqual(res_bad["grounding_status"], "UNGROUNDED")
    self.assertFalse(res_bad["allow_clinical_presentation"])

  def test_research_intelligence_registry_orchestration(self):
    graph_res = ResearchIntelligenceRegistry.assemble_evidence_graph(self.patient, "Olaparib")
    self.assertIn("evidence_graph", graph_res)
    self.assertIn("nodes", graph_res["evidence_graph"])
    self.assertIn("edges", graph_res["evidence_graph"])
    self.assertIn("claims", graph_res)

    lit_res = ResearchIntelligenceRegistry.query_literature({"query": "BRCA1 Olaparib", "patient": self.patient})
    self.assertIn("publications", lit_res)

    guide_res = ResearchIntelligenceRegistry.evaluate_guidelines({"patient": self.patient})
    self.assertIn("matched_recommendations", guide_res)

    prov_res = ResearchIntelligenceRegistry.trace_provenance({"patient": self.patient})
    self.assertIn("lineage_manifests", prov_res)
    self.assertIn("lineage_root_hash", prov_res["lineage_manifests"][0])


if __name__ == '__main__':
  unittest.main()
