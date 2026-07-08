def evaluate_toxicity_profile(timeline):
  """
  Calculates the average safety margin indicator (100 - average toxicity).
  """
  if not timeline:
    return 100.0
  avg_tox = sum(pt["toxicity"] for pt in timeline) / len(timeline)
  # Scale to percentage (toxicity is generally in [0.0, 1.0])
  return max(0.0, 100.0 - (avg_tox * 100.0))
