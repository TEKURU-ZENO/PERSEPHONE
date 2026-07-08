import numpy as np

def encode_patient_features(patient):
  """
  Encodes non-state demographics (e.g. stage, diagnosis) into feature metrics.
  """
  # Yields basic feature indicators
  is_ovarian = 1.0 if "Ovarian" in patient.diagnosis else 0.0
  is_stage_3 = 1.0 if "III" in patient.stage else 0.0
  return np.array([is_ovarian, is_stage_3], dtype=np.float32)
