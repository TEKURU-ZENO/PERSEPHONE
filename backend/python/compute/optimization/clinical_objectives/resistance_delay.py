def evaluate_resistance_suppression(timeline):
  """
  Calculates the capacity to suppress resistant clone selections.
  """
  if not timeline:
    return 100.0
  final_pt = timeline[-1]
  resistant_fraction = final_pt["resistant"] / final_pt["totalVolume"] if final_pt["totalVolume"] > 0 else 0.0
  return max(0.0, 100.0 - (resistant_fraction * 100.0))
