def get_toxicity_reward(toxicity, safe_limit=0.50):
  """
  Penalizes toxicity values exceeding clinical safety thresholds.
  """
  excess = max(0.0, toxicity - safe_limit)
  return -10.0 * excess
