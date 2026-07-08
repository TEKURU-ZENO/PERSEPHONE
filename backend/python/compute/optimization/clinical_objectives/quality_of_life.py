def evaluate_quality_of_life(timeline):
  """
  Estimates QoL indicators based on treatment holiday ratios (dosing holds).
  """
  if not timeline:
    return 100.0
  holiday_steps = sum(1 for pt in timeline if pt["dose"] == 0.0)
  # Percentage of days patient was on treatment holidays
  return (holiday_steps / len(timeline)) * 100.0
