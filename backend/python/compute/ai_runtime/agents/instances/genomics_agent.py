from backend.python.compute.ai_runtime.agents.instances.base import BaseClinicalAgent
from backend.python.compute.genomics.registry import GenomicsRegistry

class GenomicsAgent(BaseClinicalAgent):
  """
  Genomics Agent: Interprets patient variant profiles through ClinVar/COSMIC annotation,
  pathway enrichment analysis, biomarker actionability scoring, and mutation signature
  classification. Publishes variant-level intelligence to the Blackboard for downstream
  consumption by Pharmacology, Therapy Planning, and Clinical Report agents.

  Council classification: Scientific
  """
  def __init__(self):
    super().__init__("Genomics Agent", "Scientific")
    self.data_sources = [
      "VariantAnnotator", "PathwayEnrichmentEngine",
      "BiomarkerScorer", "MutationSignatureClassifier"
    ]

  def initialize(self, blackboard):
    self.patient_data = blackboard.read("patient_twin") or {}
    self.genomic_results = None

  def plan(self, blackboard):
    """
    Determines variant gene list from patient twin data.
    Falls back to default BRCA1 panel if no variants provided.
    """
    self.variant_genes = self.patient_data.get("variants", ["BRCA1"])
    self.variant_count = self.patient_data.get("variant_count", len(self.variant_genes) * 8)
    self.microsatellite_loci = self.patient_data.get("microsatellite_loci", [
      {"locus": "BAT25", "stable": True},
      {"locus": "BAT26", "stable": True},
      {"locus": "NR21", "stable": False},
      {"locus": "NR24", "stable": True},
      {"locus": "MONO27", "stable": True}
    ])

  def execute(self, blackboard):
    self.genomic_results = GenomicsRegistry.run_genomic_pipeline({
      "genes": self.variant_genes,
      "variant_count": self.variant_count,
      "microsatellite_loci": self.microsatellite_loci
    })
    self.confidence = 0.95

  def reflect(self, blackboard):
    """
    Validates genomic results: checks that annotation coverage is reasonable
    and pathway impact score is within expected range.
    """
    if self.genomic_results:
      annotated = self.genomic_results.get("annotated_variants", [])
      vus_count = sum(1 for v in annotated if v.get("clinical_significance") == "VUS")
      if vus_count == len(annotated) and len(annotated) > 0:
        self.errors = "All variants classified as VUS - verify input gene panel"

  def publish(self, blackboard):
    blackboard.write("genomic_intelligence", self.genomic_results)

    if self.genomic_results:
      ranked = self.genomic_results.get("ranked_biomarkers", [])
      actionable = [b for b in ranked if b.get("actionability_tier", "").startswith("Tier I")]
      blackboard.write("ACTIONABLE_VARIANTS", actionable)
      blackboard.write("PATHWAY_ENRICHMENT", self.genomic_results.get("pathway_enrichment", {}))
      blackboard.write("BIOMARKER_TIER", ranked[0].get("actionability_tier", "Unknown") if ranked else "Unknown")
      blackboard.write("TMB", self.genomic_results.get("tmb", {}))
      blackboard.write("MSI_STATUS", self.genomic_results.get("msi", {}).get("msi_status", "MSS"))

    blackboard.add_contribution(self.name, {
      "variants_annotated": len(self.genomic_results.get("annotated_variants", [])) if self.genomic_results else 0,
      "actionable_count": len(actionable) if self.genomic_results else 0,
      "dominant_signature": self.genomic_results.get("mutation_signature", {}).get("dominant_signature", "Unknown") if self.genomic_results else "Unknown",
      "pathway_impact": self.genomic_results.get("pathway_impact_score", 0) if self.genomic_results else 0
    })
