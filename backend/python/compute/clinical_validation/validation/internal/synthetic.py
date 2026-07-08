import numpy as np

def generate_synthetic_noise(clean_volumes, noise_level=0.05, seed=42):
  """
  Injects random noise to model cohort variance.
  """
  np.random.seed(seed)
  volumes = np.array(clean_volumes, dtype=np.float64)
  noise = np.random.normal(0.0, noise_level * volumes)
  noisy_volumes = np.maximum(10.0, volumes + noise)
  return noisy_volumes.tolist()
