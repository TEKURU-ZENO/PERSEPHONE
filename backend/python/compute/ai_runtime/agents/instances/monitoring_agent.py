from backend.python.compute.ai_runtime.agents.instances.base import BaseClinicalAgent
from backend.python.compute.monitoring.monitor import ClinicalMonitor

class ClinicalMonitoringAgent(BaseClinicalAgent):
  """
  Clinical Monitoring Agent: Tracks patient change over time across treatment cycles,
  volumetric tumor trajectories, RECIST 1.1 response status, CTCAE toxicities,
  serum/ctDNA biomarker kinetics, and early molecular progression signals.

  Council classification: Clinical
  """
  def __init__(self):
    super().__init__("Clinical Monitoring Agent", "Clinical")
    self.data_sources = [
      "ClinicalMonitor", "PatientTimeline",
      "TumorTrajectoryAnalyzer", "TreatmentResponseEvaluator",
      "ToxicityTracker", "BiomarkerKineticsAnalyzer",
      "ProgressionDetector", "ClinicalAlertGenerator"
    ]

  def initialize(self, blackboard):
    self.patient_data = blackboard.read("patient_twin") or {}
    self.sim_results = blackboard.read("simulation_results") or {}
    self.monitoring_results = None

  def plan(self, blackboard):
    """
    Formulates longitudinal evaluation scope using patient identifier.
    """
    self.patient_id = self.patient_data.get("id", "patient-a")

  def execute(self, blackboard):
    self.monitoring_results = ClinicalMonitor.evaluate_patient_state(self.patient_id)
    self.confidence = 0.96

  def reflect(self, blackboard):
    """
    Audits for critical safety alerts or progression flags requiring immediate escalation.
    """
    if self.monitoring_results:
      alerts = self.monitoring_results.get("alerts", [])
      crit = [a for a in alerts if a.get("severity") == "CRITICAL"]
      if crit:
        self.errors = f"URGENT: {len(crit)} critical monitoring alert(s) detected: {crit[0].get('title')}"

  def publish(self, blackboard):
    res = self.monitoring_results or {}

    # Exact publications specified for Phase 15
    blackboard.write("LONGITUDINAL_STATE", res)
    blackboard.write("TUMOR_TRAJECTORY", res.get("trajectory", {}))
    blackboard.write("RESPONSE_STATUS", res.get("response", {}))
    blackboard.write("TOXICITY_TRAJECTORY", res.get("toxicity", {}))
    blackboard.write("PROGRESSION_SIGNAL", res.get("progression", {}))
    blackboard.write("BIOMARKER_TRAJECTORY", res.get("biomarkers", {}))
    blackboard.write("MONITORING_ALERTS", res.get("alerts", []))

    summary = res.get("summaryMetrics", {})
    blackboard.add_contribution(self.name, {
      "currentVolume": summary.get("currentVolume", 0.0),
      "currentVelocity": summary.get("currentVelocity", 0.0),
      "bestResponse": summary.get("bestResponse", "NE"),
      "currentResponse": summary.get("currentResponse", "NE"),
      "progressionSignal": summary.get("progressionSignal", "ACTIVE_RESPONSE"),
      "alertCount": summary.get("totalAlerts", 0)
    })
