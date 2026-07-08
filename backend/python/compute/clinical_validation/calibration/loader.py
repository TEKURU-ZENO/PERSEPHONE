def load_clinical_cohort_timeline(patient_id):
  """
  Yields observed longitudinal days and total tumor volumes for calibration fitting.
  """
  # Elena Rostova observed tumor shrinkage timeline
  if patient_id == "patient-a":
    return [
      {"day": 0, "volume": 82.0},
      {"day": 7, "volume": 76.5},
      {"day": 14, "volume": 68.2},
      {"day": 28, "volume": 59.7},
      {"day": 42, "volume": 51.1},
      {"day": 56, "volume": 44.8},
      {"day": 70, "volume": 41.2},
      {"day": 90, "volume": 38.5}
    ]
  # Default patient twin values
  return [
    {"day": 0, "volume": 80.0},
    {"day": 14, "volume": 72.0},
    {"day": 28, "volume": 64.0},
    {"day": 42, "volume": 57.0},
    {"day": 56, "volume": 51.0},
    {"day": 70, "volume": 48.0}
  ]
