def get_tumor_reward(total_volume):
  """
  Penalizes tumor cell burden (minimizing total volume).
  """
  # Penalize proportional to total volume
  return -0.05 * total_volume
