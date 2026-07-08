def get_survival_reward(is_alive, is_dosing=False):
  """
  Provides reward for maintaining patient survival, while favoring treatment holidays (dosing savings).
  """
  reward = 0.0
  if is_alive:
    reward += 1.0 # Base survival step bonus
    if not is_dosing:
      reward += 0.5 # Additional dose sparing bonus (treatment holiday encouragement)
  return reward
