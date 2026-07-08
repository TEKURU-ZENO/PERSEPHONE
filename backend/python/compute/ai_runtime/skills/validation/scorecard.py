from backend.python.compute.clinical_validation.validation.metrics import calculate_goodness_of_fit

class ValidationScorecardSkill:
  """
  Skill executing goodness-of-fit validation metrics.
  """
  @staticmethod
  def compute_goodness_metrics(observed_vols, simulated_vols):
    return calculate_goodness_of_fit(observed_vols, simulated_vols)
