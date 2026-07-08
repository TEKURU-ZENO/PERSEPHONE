class PatientTwin:
  def __init__(self, patient_id, name, stage, diagnosis, variants=None, clinical_metrics=None):
    self.patient_id = patient_id
    self.name = name
    self.stage = stage
    self.diagnosis = diagnosis
    self.variants = variants or []
    self.clinical_metrics = clinical_metrics or {}

  @classmethod
  def from_json(cls, data):
    return cls(
      patient_id=data.get('id', ''),
      name=data.get('name', ''),
      stage=data.get('stage', ''),
      diagnosis=data.get('diagnosis', ''),
      variants=data.get('genomics', {}).get('variants', []),
      clinical_metrics=data.get('clinicalMetrics', {})
    )

  def to_json(self):
    return {
      "id": self.patient_id,
      "name": self.name,
      "stage": self.stage,
      "diagnosis": self.diagnosis,
      "genomics": { "variants": self.variants },
      "clinicalMetrics": self.clinical_metrics
    }
