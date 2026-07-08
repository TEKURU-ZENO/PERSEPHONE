import random
from collections import deque

class ReplayBuffer:
  """
  Transition experience replay memory buffer.
  """
  def __init__(self, capacity=1000):
    self.buffer = deque(maxlen=capacity)

  def push(self, state, action, reward, next_state, done):
    self.buffer.append((state, action, reward, next_state, done))

  def sample(self, batch_size):
    transitions = random.sample(self.buffer, batch_size)
    # unzip
    states, actions, rewards, next_states, dones = zip(*transitions)
    return states, actions, rewards, next_states, dones

  def __len__(self):
    return len(self.buffer)
