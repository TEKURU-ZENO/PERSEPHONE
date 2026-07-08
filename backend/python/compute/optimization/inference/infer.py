from backend.python.compute.optimization.environment.tumor_env import TumorEvolutionEnv
from backend.python.compute.optimization.inference.policy_loader import load_policy_regimen

def run_policy_inference(patient, policy_name, control_params=None):
  """
  Runs a forward step-by-step simulation of a patient twin under a specific policy.
  """
  env = TumorEvolutionEnv(patient, control_params)
  policy = load_policy_regimen(policy_name, patient.patient_id)
  
  obs = env.reset()
  done = False
  
  timeline = []
  cumulative_dose = 0.0
  time_to_progression = env.duration
  
  while not done:
    # 1. Action selection
    action_idx = policy.select_action(obs)
    
    # 2. Environment step (applies safety validators internally)
    next_obs, reward, done, info = env.step(action_idx)
    
    # Record stats
    SS, SR, total_vol, drug_conc, toxicity, norm_time = obs
    actual_day = float(norm_time * env.duration)
    actual_dose = float(info["actualDose"])
    
    cumulative_dose += actual_dose
    
    # Check progression
    if time_to_progression == env.duration and total_vol > env.progression_threshold and actual_day > 10:
      time_to_progression = float(actual_day)

    timeline.append({
      "day": round(actual_day, 1),
      "sensitive": round(float(SS), 4),
      "resistant": round(float(SR), 4),
      "totalVolume": round(float(total_vol), 4),
      "drugConcentration": round(float(drug_conc), 5),
      "toxicity": round(float(toxicity), 4),
      "dose": actual_dose,
      "safetyOverride": info["safetyOverride"],
      "violations": info["violations"]
    })
    
    obs = next_obs

  return {
    "timeline": timeline,
    "timeToProgression": time_to_progression,
    "maxToxicity": round(float(max(pt["toxicity"] for pt in timeline)), 2) if timeline else 0.0,
    "cumulativeDose": round(float(cumulative_dose), 2)
  }
