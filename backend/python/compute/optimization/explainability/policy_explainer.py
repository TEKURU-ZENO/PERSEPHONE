def explain_policy_action(policy_name, state, action_dose, safety_override):
  """
  Provides text explanations for action selections under active policies.
  """
  SS, SR, total, drug, toxicity, time = state
  if safety_override:
    return "Action overridden to 0.0 (Treatment Holiday). Reason: Safety constraints exceeded (high toxicity or clearance decline)."
  
  if action_dose == 0.0:
    return "Action is 0.0 (Treatment Holiday) to allow sensitive clones to compete with and suppress resistant populations."
  
  return f"Action is {action_dose:.2f} units to suppress active tumor burden under carrying capacity constraints."
