class ObservationNormalizer:
  """
  Scales high-dimensional observation vectors for stable PyTorch neural training.
  """
  def __init__(self, carry_capacity=200.0):
    self.carry_capacity = carry_capacity

  def normalize(self, obs):
    # obs = [SS, SR, total, drug, toxicity, norm_time]
    normalized = obs.copy()
    normalized[0] /= self.carry_capacity
    normalized[1] /= self.carry_capacity
    normalized[2] /= self.carry_capacity
    return normalized
