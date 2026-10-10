from backend.python.compute.simulation.params import get_default_model_params

KNOWN_PATIENT_PARAMS = {
    "patient-a": {
        "alpha1": 0.08, "alpha2": 0.045, "K": 200.0, "ES": 0.16, "ER": 0.015,
        "ke": 0.15, "beta": 0.25, "gamma": 0.10, "aSR": 1.0, "aRS": 1.0,
        "SS_init": 80.0, "SR_init": 2.0
    },
    "patient-b": {
        "alpha1": 0.06, "alpha2": 0.035, "K": 150.0, "ES": 0.12, "ER": 0.01,
        "ke": 0.15, "beta": 0.25, "gamma": 0.10, "aSR": 1.0, "aRS": 1.0,
        "SS_init": 65.0, "SR_init": 15.0
    },
    "patient-c": {
        "alpha1": 0.07, "alpha2": 0.04, "K": 180.0, "ES": 0.10, "ER": 0.015,
        "ke": 0.15, "beta": 0.25, "gamma": 0.10, "aSR": 1.0, "aRS": 1.0,
        "SS_init": 70.0, "SR_init": 10.0
    }
}

class PatientTwin:
  def __init__(self, patient_id, name, stage, diagnosis, variants=None, clinical_metrics=None, model_params=None):
    self.patient_id = patient_id
    self.name = name
    self.stage = stage
    self.diagnosis = diagnosis
    self.variants = variants or []
    self.clinical_metrics = clinical_metrics or {}
    self.model_params = model_params if model_params is not None else KNOWN_PATIENT_PARAMS.get(patient_id, {}).copy()

  @classmethod
  def from_json(cls, data):
    pid = data.get('id', '')
    p_params = data.get('modelParams') or data.get('model_params')
    if not p_params and pid in KNOWN_PATIENT_PARAMS:
      p_params = KNOWN_PATIENT_PARAMS[pid].copy()

    return cls(
      patient_id=pid,
      name=data.get('name', ''),
      stage=data.get('stage', ''),
      diagnosis=data.get('diagnosis', ''),
      variants=data.get('genomics', {}).get('variants', []),
      clinical_metrics=data.get('clinicalMetrics', {}),
      model_params=p_params or {}
    )

  def to_json(self):
    return {
      "id": self.patient_id,
      "name": self.name,
      "stage": self.stage,
      "diagnosis": self.diagnosis,
      "genomics": { "variants": self.variants },
      "clinicalMetrics": self.clinical_metrics,
      "modelParams": self.model_params
    }
