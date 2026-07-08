import unittest
import torch
import numpy as np
from backend.python.compute.optimization.algorithms.dqn import DQNNetwork
from backend.python.compute.optimization.algorithms.ppo import ActorCriticNetwork
from backend.python.compute.optimization.policies.reinforcement.dqn_policy import DQNPolicy
from backend.python.compute.optimization.policies.reinforcement.ppo_policy import PPOPolicy
from backend.python.compute.optimization.training.replay_buffer import ReplayBuffer

class TestOncologyRLAgent(unittest.TestCase):
  def test_dqn_forward(self):
    model = DQNNetwork()
    state = torch.randn(2, 6)
    q_values = model(state)
    self.assertEqual(q_values.shape, (2, 5))

  def test_ppo_forward(self):
    model = ActorCriticNetwork()
    state = torch.randn(2, 6)
    probs, value = model(state)
    self.assertEqual(probs.shape, (2, 5))
    self.assertEqual(value.shape, (2, 1))

  def test_replay_buffer_pushes(self):
    buf = ReplayBuffer(capacity=10)
    state = np.zeros(6, dtype=np.float32)
    next_state = np.ones(6, dtype=np.float32)
    
    buf.push(state, 1, 10.0, next_state, False)
    self.assertEqual(len(buf), 1)
    
    states, actions, rewards, next_states, dones = buf.sample(1)
    self.assertEqual(actions[0], 1)
    self.assertEqual(rewards[0], 10.0)

  def test_policy_argmax_evaluations(self):
    dqn_policy = DQNPolicy()
    ppo_policy = PPOPolicy()
    
    state = [80.0, 2.0, 82.0, 0.0, 0.0, 0.0]
    dqn_act = dqn_policy.select_action(state)
    ppo_act = ppo_policy.select_action(state)
    
    self.assertTrue(0 <= dqn_act <= 4)
    self.assertTrue(0 <= ppo_act <= 4)

if __name__ == '__main__':
  unittest.main()
