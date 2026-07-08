from backend.python.compute.clinical_validation.calibration.loader import load_clinical_cohort_timeline

class ClinicalMemorySearchSkill:
  """
  Skill scanning historical recommendations database.
  """
  @staticmethod
  def load_historical_timeline(patient_twin):
    try:
      return load_clinical_cohort_timeline(patient_twin.patient_id)
    except Exception:
      # Fallback
      return [
        {"day": 0, "volume": 80.0},
        {"day": 14, "volume": 72.0},
        {"day": 28, "volume": 60.0}
      ]
