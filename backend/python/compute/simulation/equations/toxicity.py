# Pharmacodynamics (PD) Toxicity Model
from shared.math.constants import TOX_ACCUMULATION, TOX_DECAY

def evaluate_toxicity_accumulation(current_tox, concentration):
  """
  Calculates systemic toxicity accumulation based on drug concentration.
  """
  new_tox = current_tox + TOX_ACCUMULATION * concentration - TOX_DECAY * current_tox
  return max(0.0, new_tox)
