from backend.python.compute.optimization.policies.registry import PolicyRegistry

def load_policy_regimen(policy_name, patient_id=None):
  """
  Retrieves a treatment policy, loading checkpoint weights if required.
  """
  kwargs = {}
  if policy_name in ["dqn", "ppo"] and patient_id:
    # Set expected path
    kwargs["model_path"] = f"backend/python/checkpoints/{patient_id}_{policy_name}.pt"
    
  return PolicyRegistry.get(policy_name, **kwargs)
