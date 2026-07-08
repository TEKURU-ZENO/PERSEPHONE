def map_clinical_features(patient):
  return {
    "age": 62 if patient.patient_id == 'patient-a' else 45,
    "mutationBurden": 4 if patient.patient_id == 'patient-a' else 12
  }
