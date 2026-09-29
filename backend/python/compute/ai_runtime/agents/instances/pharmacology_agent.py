from backend.python.compute.ai_runtime.agents.instances.base import BaseClinicalAgent
from backend.python.compute.pharmacogenomics.registry import PharmacogenomicsRegistry

class PharmacologyAgent(BaseClinicalAgent):
  """
  Pharmacology Agent: Resolves drug-gene interactions, predicts drug sensitivity
  via IC50 modeling, maps resistance mechanisms and bypass pathways, and estimates
  combination synergy scores. Publishes drug intelligence to the Blackboard for
  downstream consumption by Therapy Planning, Safety, and Clinical Report agents.

  Council classification: Clinical
  """
  def __init__(self):
    super().__init__("Pharmacology Agent", "Clinical")
    self.data_sources = [
      "DrugGeneResolver", "SensitivityPredictor",
      "ResistanceMapper", "SynergyEstimator"
    ]

  def initialize(self, blackboard):
    self.patient_data = blackboard.read("patient_twin") or {}
    self.genomic_intel = blackboard.read("genomic_intelligence") or {}
    self.pharma_results = None

  def plan(self, blackboard):
    """
    Determines gene variants from genomic intelligence or patient twin data.
    Drug candidates are auto-discovered from the interaction DB.
    """
    annotated = self.genomic_intel.get("annotated_variants", [])
    if annotated:
      self.gene_variants = [v.get("gene", "") for v in annotated if v.get("gene")]
    else:
      self.gene_variants = self.patient_data.get("variants", ["BRCA1"])

  def execute(self, blackboard):
    self.pharma_results = PharmacogenomicsRegistry.run_pharmacogenomics_pipeline(
      gene_variants=self.gene_variants,
      drug_candidates=None  # auto-discover from interaction DB
    )
    self.confidence = 0.93

  def reflect(self, blackboard):
    """
    Validates pharmacogenomics results: checks for contraindications that
    conflict with the current therapy plan.
    """
    if self.pharma_results:
      contras = self.pharma_results.get("contraindications", [])
      therapy_plan = blackboard.read("therapy_plan") or {}
      current_drug = therapy_plan.get("drug", "")
      for c in contras:
        if c.get("drug", "").lower() == current_drug.lower():
          self.errors = f"CRITICAL: Current therapy {current_drug} is contraindicated due to {c.get('reason', 'unknown')}"

  def publish(self, blackboard):
    blackboard.write("pharmacogenomic_profile", self.pharma_results)

    if self.pharma_results:
      blackboard.write("DRUG_SENSITIVITY_SCORES", self.pharma_results.get("ranked_drugs", []))
      blackboard.write("RESISTANCE_MECHANISMS", self.pharma_results.get("resistance_mechanisms", []))
      blackboard.write("COMBINATION_SYNERGIES", self.pharma_results.get("synergy_matrix", []))
      blackboard.write("CONTRAINDICATIONS", self.pharma_results.get("contraindications", []))

    ranked = self.pharma_results.get("ranked_drugs", []) if self.pharma_results else []
    top_drug = ranked[0] if ranked else {}
    synergies = self.pharma_results.get("synergy_matrix", []) if self.pharma_results else []
    top_synergy = synergies[0] if synergies else {}

    blackboard.add_contribution(self.name, {
      "top_drug": top_drug.get("drug", "None"),
      "top_sensitivity": top_drug.get("sensitivity_class", "unknown"),
      "resistance_count": len(self.pharma_results.get("resistance_mechanisms", [])) if self.pharma_results else 0,
      "contraindication_count": len(self.pharma_results.get("contraindications", [])) if self.pharma_results else 0,
      "top_synergy_pair": f"{top_synergy.get('drug_a', '?')} + {top_synergy.get('drug_b', '?')}" if top_synergy else "None"
    })
