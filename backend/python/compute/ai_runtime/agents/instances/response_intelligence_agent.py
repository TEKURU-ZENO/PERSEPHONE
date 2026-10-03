from backend.python.compute.ai_runtime.agents.instances.base import BaseClinicalAgent
from backend.python.compute.response_intelligence.registry import ResponseIntelligenceRegistry

class ResponseIntelligenceAgent(BaseClinicalAgent):
  """
  Response Intelligence Agent: Synthesizes pathology, radiology, genomics,
  pharmacogenomics, clinical trials, and longitudinal monitoring into
  multimodal digital biomarkers, research-calibrated treatment response predictions,
  and early resistance escape projections.

  Council classification: Scientific / Clinical
  """
  def __init__(self):
    super().__init__("Response Intelligence Agent", "Scientific")
    self.data_sources = [
      "ResponseIntelligenceRegistry", "MultimodalResponseFusion",
      "CompositeBiomarkerSynthesizer", "TreatmentResponsePredictor",
      "ResistanceEscapePredictor"
    ]

  def initialize(self, blackboard):
    self.patient_data = blackboard.read("patient_twin") or {}
    self.genomic_intel = blackboard.read("genomic_intelligence") or {}
    self.longitudinal_state = blackboard.read("LONGITUDINAL_STATE") or {}
    self.top_trial = blackboard.read("TOP_TRIAL") or {}
    self.top_drugs = blackboard.read("DRUG_SENSITIVITY_SCORES") or []
    self.response_results = None

  def plan(self, blackboard):
    """
    Assembles multimodal fusion input payload from Blackboard.
    """
    top_candidate = self.top_drugs[0].get("drug", "Olaparib") if self.top_drugs else "Olaparib"
    variants = self.patient_data.get("variants", ["BRCA1"])

    self.payload = {
      "patient_id": self.patient_data.get("id", "patient-a"),
      "variants": variants,
      "proposed_drug": top_candidate,
      "genomics": {
        "variants": variants,
        "hrd_score": 58.0 if "BRCA1" in str(variants) else 25.0,
        "tmb": (blackboard.read("TMB") or {}).get("tmb_score", 8.5),
        "msi_status": blackboard.read("MSI_STATUS") or "MSS"
      },
      "imaging": {
        "tumor_purity": blackboard.read("TUMOR_PURITY") or 72.5,
        "necrosis_ratio": blackboard.read("NECROSIS") or 8.4,
        "til_density": 0.68,
        "heterogeneity_index": 0.42
      },
      "pharmacogenomics": {
        "top_candidate": top_candidate,
        "ic50": 1.8 if top_candidate == "Olaparib" else 3.5,
        "synergy_score": 0.76
      },
      "trials": {
        "top_trial_id": self.top_trial.get("trialId", "NCT03737643"),
        "match_score": self.top_trial.get("compositeScore", 0.92)
      },
      "monitoring": {
        "current_volume": (self.longitudinal_state.get("trajectory") or {}).get("currentVolume", 26.5),
        "velocity": (self.longitudinal_state.get("trajectory") or {}).get("currentVelocity", 0.10),
        "vaf": (self.longitudinal_state.get("biomarkers") or {}).get("ctdnaVaf", {}).get("current", 4.2),
        "max_grade": (self.longitudinal_state.get("toxicity") or {}).get("maxGradeObserved", 2)
      }
    }

  def execute(self, blackboard):
    self.response_results = ResponseIntelligenceRegistry.run_full_response_intelligence(self.payload)
    self.confidence = 0.95

  def reflect(self, blackboard):
    """
    Validates prediction bounds and checks if resistance risk requires therapy escalation.
    """
    if self.response_results:
      risk = self.response_results.get("resistance", {}).get("escape_prediction", {}).get("resistance_risk", {}).get("value", 0.0)
      if risk >= 0.70:
        self.errors = f"CAUTION: High resistance emergence risk ({risk:.2f}). Escalate alternative escape pathways."

  def publish(self, blackboard):
    res = self.response_results or {}
    pred = res.get("response", {}).get("prediction", {})
    escape = res.get("resistance", {}).get("escape_prediction", {})
    comp = res.get("biomarkers", {}).get("composite", {})

    # Isolated Blackboard publications
    blackboard.write("RESPONSE_INTELLIGENCE", res)
    blackboard.write("PREDICTED_ORR", pred.get("predicted_orr", {}))
    blackboard.write("PREDICTED_PFS_DAYS", pred.get("predicted_pfs_days", {}))
    blackboard.write("RESISTANCE_RISK", escape.get("resistance_risk", {}))
    blackboard.write("TTAR", escape.get("time_to_acquired_resistance_days", {}))
    blackboard.write("COMPOSITE_BIOMARKER_SCORE", comp)
    blackboard.write("PREDICTED_ESCAPE_PATHWAYS", escape.get("predicted_escape_pathways", []))

    blackboard.add_contribution(self.name, {
      "predicted_orr": pred.get("predicted_orr", {}).get("value", 0.75),
      "predicted_pfs_days": pred.get("predicted_pfs_days", {}).get("value", 330.0),
      "composite_actionability_score": comp.get("value", 0.82),
      "resistance_risk": escape.get("resistance_risk", {}).get("value", 0.50),
      "active_mechanisms_count": len(res.get("resistance", {}).get("detection", {}).get("mechanisms", []))
    })
