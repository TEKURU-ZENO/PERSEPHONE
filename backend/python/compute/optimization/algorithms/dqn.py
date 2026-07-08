import torch
import torch.nn as nn

class DQNNetwork(nn.Module):
  """
  Deep Q-Network for discrete actions over continuous oncology spaces.
  """
  def __init__(self, state_dim=6, action_dim=5):
    super().__init__()
    self.net = nn.Sequential(
      nn.Linear(state_dim, 32),
      nn.ReLU(),
      nn.Linear(32, 32),
      nn.ReLU(),
      nn.Linear(32, action_dim)
    )

  def forward(self, x):
    if not isinstance(x, torch.Tensor):
      x = torch.tensor(x, dtype=torch.float32)
    return self.net(x)
