from backend.python.compute.optimization.policies.base import BasePolicy

class MetronomicPolicy(BasePolicy):
  """
  Constant low-dose metronomic strategy.
  """
  def __init__(self):
    super().__init__("metronomic")

  def select_action(self, state):
    # Continuous lower dosing
    return 1 # Action 1 corresponding to 0.25 (Continuous Low-Dose)
