class SimulationRequest:
  def __init__(self, patient, strategy, control_params):
    self.patient = patient
    self.strategy = strategy
    self.control_params = control_params

  @classmethod
  def from_json(cls, data):
    from backend.python.compute.common.models.patient import PatientTwin
    return cls(
      patient=PatientTwin.from_json(data.get('patient', {})),
      strategy=data.get('strategy', 'mtd'),
      control_params=data.get('controlParams', {})
    )

class SimulationResult:
  def __init__(self, timeline, time_to_progression, max_toxicity, cumulative_dose):
    self.timeline = timeline
    self.time_to_progression = time_to_progression
    self.max_toxicity = max_toxicity
    self.cumulative_dose = cumulative_dose

  def to_json(self):
    return {
      "timeline": self.timeline,
      "timeToProgression": self.time_to_progression,
      "maxToxicity": self.max_toxicity,
      "cumulativeDose": self.cumulative_dose
    }
