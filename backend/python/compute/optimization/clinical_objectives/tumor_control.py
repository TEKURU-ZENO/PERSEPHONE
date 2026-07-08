def evaluate_tumor_control(timeline):
  """
  Calculates the average tumor burden suppression score.
  """
  if not timeline:
    return 0.0
  avg_burden = sum(pt["totalVolume"] for pt in timeline) / len(timeline)
  # Normalized score (0-100), higher is better
  return max(0.0, 100.0 - avg_burden)
