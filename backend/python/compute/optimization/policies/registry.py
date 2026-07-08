# Pluggable Policy Registry
from backend.python.compute.optimization.policies.rule_based.mtd import MTDPolicy
from backend.python.compute.optimization.policies.rule_based.metronomic import MetronomicPolicy
from backend.python.compute.optimization.policies.rule_based.adaptive import AdaptivePolicy
from backend.python.compute.optimization.policies.reinforcement.dqn_policy import DQNPolicy
from backend.python.compute.optimization.policies.reinforcement.ppo_policy import PPOPolicy

class PolicyRegistry:
  _REGISTRY = {}

  @classmethod
  def register(cls, key, policy_instance):
    cls._REGISTRY[key] = policy_instance

  @classmethod
  def get(cls, key, **kwargs):
    # Default initializations
    if key == "mtd":
      return MTDPolicy()
    elif key == "metronomic":
      return MetronomicPolicy()
    elif key == "adaptive":
      initial_vol = kwargs.get("initial_total", 82.0)
      return AdaptivePolicy(initial_total=initial_vol)
    elif key == "dqn":
      return DQNPolicy(model_path=kwargs.get("model_path"))
    elif key == "ppo":
      return PPOPolicy(model_path=kwargs.get("model_path"))
    
    return cls._REGISTRY.get(key)

  @classmethod
  def list_policies(cls):
    return ["mtd", "metronomic", "adaptive", "dqn", "ppo"]
