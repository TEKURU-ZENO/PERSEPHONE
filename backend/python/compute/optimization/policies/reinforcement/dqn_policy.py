import torch
from backend.python.compute.optimization.policies.base import BasePolicy
from backend.python.compute.optimization.algorithms.dqn import DQNNetwork

class DQNPolicy(BasePolicy):
  """
  Trained DQN Policy evaluator.
  """
  def __init__(self, model_path=None):
    super().__init__("dqn")
    self.model = DQNNetwork()
    if model_path:
      try:
        self.model.load_state_dict(torch.load(model_path))
      except Exception:
        pass
    self.model.eval()

  def select_action(self, state):
    with torch.no_grad():
      state_t = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
      q_values = self.model(state_t)
      return int(q_values.argmax(dim=-1).item())
