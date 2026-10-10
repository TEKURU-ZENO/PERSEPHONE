# Pharmacodynamics (PD) Toxicity Model
from backend.python.compute.simulation.params import get_default_model_params

_defaults = get_default_model_params()
TOX_ACCUMULATION = _defaults.get("beta", 0.25)
TOX_DECAY = _defaults.get("gamma", 0.10)

def evaluate_toxicity_accumulation(current_tox, concentration, beta=None, gamma=None):
  """
  Calculates systemic toxicity accumulation based on drug concentration.
  """
  b = beta if beta is not None else TOX_ACCUMULATION
  g = gamma if gamma is not None else TOX_DECAY
  new_tox = current_tox + b * concentration - g * current_tox
  return max(0.0, new_tox)
