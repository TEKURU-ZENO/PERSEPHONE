# Pharmacokinetics (PK) Model
from backend.python.compute.simulation.params import get_default_model_params

_defaults = get_default_model_params()
CLEARANCE_RATE = _defaults.get("ke", 0.15)

def evaluate_pk_concentration(current_conc, dose, clearance_rate=None):
  """
  Calculates drug concentration decay and dose additions.
  """
  ke = clearance_rate if clearance_rate is not None else CLEARANCE_RATE
  return current_conc * (1.0 - ke) + dose
