from backend.python.compute.optimization.environment.reward.tumor import get_tumor_reward
from backend.python.compute.optimization.environment.reward.toxicity import get_toxicity_reward
from backend.python.compute.optimization.environment.reward.survival import get_survival_reward

class CompositeReward:
  """
  Clinical objective function aggregating multi-factor objectives.
  """
  @staticmethod
  def calculate(total_volume, toxicity, is_alive, is_dosing):
    r_tumor = get_tumor_reward(total_volume)
    r_tox = get_toxicity_reward(toxicity)
    r_surv = get_survival_reward(is_alive, is_dosing)
    
    return r_tumor + r_tox + r_surv
