from backend.python.compute.optimization.policies.base import BasePolicy

class AdaptivePolicy(BasePolicy):
  """
  Gatenby threshold-based adaptive treatment holiday policy.
  """
  def __init__(self, interval=7, initial_total=82.0):
    super().__init__("adaptive")
    self.interval = interval
    self.initial_total = initial_total
    self.is_holiday = False

  def select_action(self, state):
    # state[2] is total tumor volume
    total_vol = state[2]
    norm_time = state[5]
    day = round(norm_time * 180.0)

    # Dosing hold triggers
    if self.is_holiday and total_vol > 1.0 * self.initial_total:
      self.is_holiday = False
    elif not self.is_holiday and total_vol < 0.50 * self.initial_total:
      self.is_holiday = True

    if not self.is_holiday and (int(day) % self.interval == 0):
      return 4 # Full Dose
    return 0   # Holiday / Hold
