class SimulationValidator:
  @staticmethod
  def validate(request):
    """
    Validates simulation boundaries:
    - mtdDose > 0
    - initialResistantRatio between 0 and 100
    - duration > 0
    """
    params = request.control_params
    errors = []

    mtd = float(params.get('mtdDose', 10))
    ratio = float(params.get('initialResistantRatio', 10))
    duration = float(params.get('duration', 180))

    if mtd <= 0:
      errors.append("MTD Dose must be greater than 0.")
    if ratio < 0 or ratio > 100:
      errors.append("Initial Resistant Ratio must be between 0 and 100.")
    if duration <= 0:
      errors.append("Simulation duration must be greater than 0.")

    if errors:
      raise ValueError("Validation error: " + "; ".join(errors))
    return True
