import os
import torch

def save_checkpoint(model, filename, directory="backend/python/checkpoints/"):
  """
  Saves model parameters safely.
  """
  if not os.path.exists(directory):
    os.makedirs(directory)
  path = os.path.join(directory, filename)
  torch.save(model.state_dict(), path)
  return path

def load_checkpoint(model, filename, directory="backend/python/checkpoints/"):
  """
  Loads weights if existing.
  """
  path = os.path.join(directory, filename)
  if os.path.exists(path):
    model.load_state_dict(torch.load(path))
    return True
  return False
