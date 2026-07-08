import os
import json

class ExperimentTracker:
  """
  Lightweight run logger for oncology optimization runs.
  """
  @staticmethod
  def create_run_directory(base_dir="backend/python/experiments/runs/"):
    if not os.path.exists(base_dir):
      os.makedirs(base_dir)
      
    # Scan for existing RUN folders
    existing_runs = [d for d in os.listdir(base_dir) if d.startswith("RUN-")]
    run_num = len(existing_runs) + 1
    run_name = f"RUN-{run_num:03d}"
    
    run_path = os.path.join(base_dir, run_name)
    os.makedirs(run_path)
    return run_path, run_name

  @staticmethod
  def log_experiment_run(patient, policy_name, metrics, rewards, losses, hyperparameters=None):
    run_path, run_name = ExperimentTracker.create_run_directory()
    
    # Save metadata
    metadata = {
      "runName": run_name,
      "policyName": policy_name,
      "patientId": patient.patient_id,
      "hyperparameters": hyperparameters or {},
      "finalMetrics": metrics
    }
    
    with open(os.path.join(run_path, "metadata.json"), "w") as f:
      json.dump(metadata, f, indent=2)
      
    # Save reward/loss history curves
    with open(os.path.join(run_path, "reward_curves.csv"), "w") as f:
      f.write("epoch,reward,loss\n")
      for idx in range(len(rewards)):
        loss_val = losses[idx] if idx < len(losses) else 0.0
        f.write(f"{idx},{rewards[idx]},{loss_val}\n")
        
    return run_name
