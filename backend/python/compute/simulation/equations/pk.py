# Pharmacokinetics (PK) Model
from shared.math.constants import CLEARANCE_RATE

def evaluate_pk_concentration(current_conc, dose):
  """
  Calculates drug concentration decay and dose additions.
  """
  return current_conc * (1.0 - CLEARANCE_RATE) + dose
