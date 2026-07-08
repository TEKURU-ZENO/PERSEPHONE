import numpy as np

def build_observation(SS, SR, drug, toxicity, step, max_steps):
  """
  Packs clinical parameters into a standardized 6D NumPy observation vector.
  """
  total = SS + SR
  norm_time = float(step) / float(max_steps) if max_steps > 0 else 0.0
  return np.array([SS, SR, total, drug, toxicity, norm_time], dtype=np.float32)
