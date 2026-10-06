import torch
import torch.nn as nn

class ActorCriticNetwork(nn.Module):
  """
  Actor-Critic network supporting continuous discretized dosing actions.
  """
  def __init__(self, state_dim=6, action_dim=5):
    super().__init__()
    self.actor = nn.Sequential(
      nn.Linear(state_dim, 32),
      nn.ReLU(),
      nn.Linear(32, action_dim),
      nn.Softmax(dim=-1)
    )
    self.critic = nn.Sequential(
      nn.Linear(state_dim, 32),
      nn.ReLU(),
      nn.Linear(32, 1)
    )

  def forward(self, x):
    if not isinstance(x, torch.Tensor):
      x = torch.tensor(x, dtype=torch.float32)
    probs = self.actor(x)
    value = self.critic(x)
    return probs, value
