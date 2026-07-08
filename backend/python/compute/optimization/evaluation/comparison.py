from backend.python.compute.optimization.inference.infer import run_policy_inference
from backend.python.compute.optimization.evaluation.metrics import evaluate_trajectory_metrics

def run_policy_comparison(patient, control_params=None):
  """
  Benchmarks all registered policies (MTD, metronomic, adaptive, RL) in parallel.
  """
  policies = ["mtd", "metronomic", "adaptive", "dqn"]
  results = {}
  
  for p in policies:
    traj = run_policy_inference(patient, p, control_params)
    scores = evaluate_trajectory_metrics(traj)
    
    results[p] = {
      "trajectory": traj,
      "metrics": scores
    }
    
  return results
