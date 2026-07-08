import torch
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
from backend.python.compute.optimization.environment.tumor_env import TumorEvolutionEnv
from backend.python.compute.optimization.algorithms.dqn import DQNNetwork
from backend.python.compute.optimization.training.replay_buffer import ReplayBuffer
from backend.python.compute.optimization.training.checkpoint import save_checkpoint

def train_optimization_policy(patient, control_params=None, epochs=5, batch_size=16):
  """
  Executes an optimization training loop on PyTorch.
  """
  env = TumorEvolutionEnv(patient, control_params)
  model = DQNNetwork()
  optimizer = optim.Adam(model.parameters(), lr=0.005)
  replay_buffer = ReplayBuffer(capacity=500)
  
  epoch_rewards = []
  epoch_losses = []
  
  for epoch in range(epochs):
    state = env.reset()
    done = False
    total_reward = 0.0
    losses = []
    
    while not done:
      # Epsilon-greedy action selection
      epsilon = max(0.1, 1.0 - (epoch * 0.15))
      if np.random.rand() < epsilon:
        action = np.random.randint(5)
      else:
        with torch.no_grad():
          state_t = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
          action = int(model(state_t).argmax(dim=-1).item())
          
      next_state, reward, done, info = env.step(action)
      replay_buffer.push(state, action, reward, next_state, done)
      state = next_state
      total_reward += reward
      
      # Perform gradient update if buffer is sufficiently filled
      if len(replay_buffer) >= batch_size:
        states, actions, rewards, next_states, dones = replay_buffer.sample(batch_size)
        
        states_t = torch.tensor(np.array(states), dtype=torch.float32)
        actions_t = torch.tensor(actions, dtype=torch.long).unsqueeze(1)
        rewards_t = torch.tensor(rewards, dtype=torch.float32).unsqueeze(1)
        next_states_t = torch.tensor(np.array(next_states), dtype=torch.float32)
        dones_t = torch.tensor(dones, dtype=torch.float32).unsqueeze(1)
        
        # Calculate loss
        q_values = model(states_t).gather(1, actions_t)
        with torch.no_grad():
          max_next_q = model(next_states_t).max(1)[0].unsqueeze(1)
          target_q = rewards_t + (1.0 - dones_t) * 0.99 * max_next_q
          
        loss = F.mse_loss(q_values, target_q)
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        losses.append(loss.item())

    epoch_rewards.append(total_reward)
    epoch_losses.append(np.mean(losses) if losses else 0.0)

  # Save trained checkpoint
  filename = f"{patient.patient_id}_dqn.pt"
  save_checkpoint(model, filename)
  
  return {
    "rewards": [round(float(r), 2) for r in epoch_rewards],
    "losses": [round(float(l), 4) for l in epoch_losses],
    "epochsCompleted": epochs
  }
