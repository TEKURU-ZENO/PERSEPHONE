import torch
from backend.python.compute.optimization.policies.base import BasePolicy
from backend.python.compute.optimization.algorithms.ppo import ActorCriticNetwork

class PPOPolicy(BasePolicy):
  """
  Trained PPO Policy evaluator.
  """
  def __init__(self, model_path=None):
    super().__init__("ppo")
    self.model = ActorCriticNetwork()
    if model_path:
      try:
        self.model.load_state_dict(torch.load(model_path))
      except Exception:
        pass
    self.model.eval()

  def select_action(self, state):
    with torch.no_grad():
      state_t = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
      probs, _ = self.model(state_t)
      return int(probs.argmax(dim=-1).item())
