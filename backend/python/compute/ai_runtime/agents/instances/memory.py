from backend.python.compute.ai_runtime.agents.instances.base import BaseClinicalAgent
from backend.python.compute.ai_runtime.skills.memory.search import ClinicalMemorySearchSkill
from backend.python.compute.common.models.patient import PatientTwin

class ClinicalMemoryAgent(BaseClinicalAgent):
  """
  Knowledge: Clinical Memory Agent retrieving patient cohort histories.
  """
  def __init__(self):
    super().__init__("Clinical Memory", "Knowledge")
    self.data_sources = ["ClinicalMemorySearchSkill", "Cohort Memory Store"]

  def initialize(self, blackboard):
    self.patient_data = blackboard.read("patient_twin") or {"id": "patient-a"}

  def plan(self, blackboard):
    pass

  def execute(self, blackboard):
    twin = PatientTwin(
      patient_id=self.patient_data.get("id"),
      name=self.patient_data.get("name", "Elena"),
      stage=self.patient_data.get("stage", "III"),
      diagnosis=self.patient_data.get("diagnosis", "Ovarian Cancer")
    )
    self.timeline = ClinicalMemorySearchSkill.load_historical_timeline(twin)
    self.confidence = 0.96

  def reflect(self, blackboard):
    pass

  def publish(self, blackboard):
    blackboard.write("clinical_memory", self.timeline)
    blackboard.add_contribution(self.name, {
      "timelineMatchesFound": len(self.timeline)
    })
