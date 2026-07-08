from backend.python.compute.optimization.environment.constraints.toxicity import verify_toxicity_limit
from backend.python.compute.optimization.environment.constraints.clearance import verify_renal_clearance

class SafetyConstraintValidator:
  """
  Clinical safety validation filter checking all active safety rules.
  """
  @staticmethod
  def validate_action(toxicity, clinical_metrics, dose_level):
    violations = []
    
    # 1. Toxicity check
    ok_tox, err_tox = verify_toxicity_limit(toxicity, dose_level)
    if not ok_tox:
      violations.append(err_tox)
      
    # 2. Clearance check
    ok_renal, err_renal = verify_renal_clearance(clinical_metrics, dose_level)
    if not ok_renal:
      violations.append(err_renal)

    return {
      "valid": len(violations) == 0,
      "violations": violations
    }
