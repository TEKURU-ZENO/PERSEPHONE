from backend.python.compute.optimization.policies.base import BasePolicy

class MTDPolicy(BasePolicy):
  """
  Standard continuous Maximum Tolerated Dose (MTD) strategy.
  """
  def __init__(self, interval=7):
    super().__init__("mtd")
    self.interval = interval

  def select_action(self, state):
    # state[-1] is normalized time. Let's compute actual day
    # total steps = 360, day = normalized_time * 180
    norm_time = state[5]
    day = round(norm_time * 180.0)
    
    # MTD is active on dosing days
    if int(day) % self.interval == 0:
      return 4 # Action 4 corresponding to 1.0 (Full Dose)
    return 0   # Holiday
