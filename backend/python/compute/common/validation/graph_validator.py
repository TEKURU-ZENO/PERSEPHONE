class GraphValidator:
  @staticmethod
  def validate(patient_id):
    """
    Validates graph path query parameters:
    - patient_id must be a non-empty string
    """
    if not patient_id or not isinstance(patient_id, str):
      raise ValueError("Validation error: Invalid patientId provided.")
    return True
