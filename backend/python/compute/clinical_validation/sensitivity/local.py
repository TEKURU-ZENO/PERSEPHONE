from backend.python.compute.clinical_validation.calibration.calibrator import evaluate_sim_mse

def run_local_sensitivity(patient, empirical_data):
  """
  Calculates local parameter derivatives via finite perturbation sweeps (+2%).
  """
  # Parameters to study: [K, alpha1, alpha2]
  base_params = [200.0, 0.08, 0.045]
  
  days = [pt["day"] for pt in empirical_data]
  true_vols = [pt["volume"] for pt in empirical_data]
  
  base_mse = evaluate_sim_mse(base_params, days, true_vols, patient)
  
  perturbation = 0.02
  sensitivities = {}
  labels = ["K (Carrying Capacity)", "alpha1 (Sensitive Growth)", "alpha2 (Resistant Growth)"]
  
  for idx, label in enumerate(labels):
    perturbed_params = base_params.copy()
    perturbed_params[idx] *= (1.0 + perturbation)
    
    new_mse = evaluate_sim_mse(perturbed_params, days, true_vols, patient)
    
    derivative = (new_mse - base_mse) / (base_params[idx] * perturbation)
    sensitivities[label] = max(0.0001, round(float(abs(derivative)), 6))
    
  # Normalize to sum = 100%
  total_sens = sum(sensitivities.values()) or 1.0
  norm_sens = {k: round((v / total_sens) * 100.0, 1) for k, v in sensitivities.items()}
  
  return norm_sens
