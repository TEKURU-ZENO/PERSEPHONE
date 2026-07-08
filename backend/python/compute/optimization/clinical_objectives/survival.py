def evaluate_progression_free_survival(time_to_progression, max_duration=180.0):
  """
  Calculates the percentage of progression-free survival duration.
  """
  return (time_to_progression / max_duration) * 100.0
