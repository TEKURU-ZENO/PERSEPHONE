# Discrete action space mappings for treatment selection bounds
ACTIONS = [0.0, 0.25, 0.50, 0.75, 1.0]

def get_action_dose(action_idx, mtd_dose=10.0):
  """
  Translates a policy action index [0, 4] to an actual dose quantity.
  """
  fraction = ACTIONS[action_idx]
  return fraction * mtd_dose
