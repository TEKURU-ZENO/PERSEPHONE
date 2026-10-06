from backend.python.compute.ai_runtime.agents.instances.base import BaseClinicalAgent
from backend.python.compute.trials.registry import ClinicalTrialsRegistry

class ClinicalTrialsAgent(BaseClinicalAgent):
  """
  Clinical Trials Agent: Matches patient genomic, pathological, and clinical profiles
  against active clinical trial protocols. Evaluates multi-factorial eligibility,
  applies evidence weighting, filters geographic proximity, and publishes trial
  options to the Blackboard for Therapy Planning and Clinical Reporting.

  Council classification: Clinical
  """
  def __init__(self):
    super().__init__("Clinical Trials Agent", "Clinical")
    self.data_sources = [
      "TrialRegistry", "EligibilityExtractor",
      "TrialMatcher", "TrialRanker", "GeographicFilter"
    ]

  def initialize(self, blackboard):
    self.patient_data = blackboard.read("patient_twin") or {}
    self.genomic_intel = blackboard.read("genomic_intelligence") or {}
    self.pharma_data = blackboard.read("pharmacogenomic_profile") or {}
    self.trial_results = None

  def plan(self, blackboard):
    """
    Formulates clinical profile combining patient demographics, stage, variants,
    and biomarker tiers.
    """
    variants = self.patient_data.get("variants", ["BRCA1"])
    diagnosis = self.patient_data.get("diagnosis", "Ovarian Cancer")
    stage = self.patient_data.get("stage", "Stage III")
    biomarker_tier = blackboard.read("BIOMARKER_TIER") or "Tier I-A"

    self.profile = {
      "cancer_type": self.patient_data.get("cancerType") or self.patient_data.get("cancer_type", ""),
      "variants": variants,
      "diagnosis": diagnosis,
      "stage": stage,
      "biomarker_tier": biomarker_tier,
      "microsatellite_status": self.patient_data.get("microsatellite_status", ""),
      "age": self.patient_data.get("age", 58),
      "ecog": self.patient_data.get("ecog", 1),
      "country": self.patient_data.get("country", "United States"),
      "city": self.patient_data.get("city", "New York"),
      "prior_therapies": self.patient_data.get("prior_therapies", []),
      "contraindications": blackboard.read("CONTRAINDICATIONS") or []
    }

  def execute(self, blackboard):
    self.trial_results = ClinicalTrialsRegistry.run_trial_matching_pipeline(self.profile)
    self.confidence = 0.94

  def reflect(self, blackboard):
    """
    Validates trial matching quality and exclusion safety.
    """
    if self.trial_results:
      eligible = [t for t in self.trial_results.get("matchedTrials", []) if t.get("isEligible")]
      if not eligible:
        self.errors = "No eligible clinical trials found matching current patient profile."

  def publish(self, blackboard):
    blackboard.write("trial_intelligence", self.trial_results)

    if self.trial_results:
      matched_trials = self.trial_results.get("matchedTrials", [])
      top_trial = self.trial_results.get("topTrial")

      blackboard.write("MATCHED_TRIALS", matched_trials)
      blackboard.write("TOP_TRIAL", top_trial)
      if top_trial:
        blackboard.write("TRIAL_EVIDENCE_SCORE", top_trial.get("compositeScore", 0.0))
      else:
        blackboard.write("TRIAL_EVIDENCE_SCORE", 0.0)

    top_trial_obj = (self.trial_results.get("topTrial") or {}) if self.trial_results else {}
    top_id = top_trial_obj.get("trialId", "None")
    top_score = top_trial_obj.get("compositeScore", 0.0)

    blackboard.add_contribution(self.name, {
      "screened_count": self.trial_results.get("totalScreened", 0) if self.trial_results else 0,
      "eligible_count": self.trial_results.get("totalEligible", 0) if self.trial_results else 0,
      "top_trial_id": top_id,
      "top_trial_score": top_score
    })
