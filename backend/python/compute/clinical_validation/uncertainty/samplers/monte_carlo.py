import numpy as np
from backend.python.compute.simulation.solvers.rk4 import rk4_step
from backend.python.compute.simulation.core.simulator import system_derivatives

def run_monte_carlo_uncertainty(patient, fitted_params, samples=50):
  """
  Runs Monte Carlo parameter sweeps around calibrated parameters to estimate 95% confidence bands.
  """
  np.random.seed(42)
  
  K_fit = fitted_params.get("K", 200.0)
  a1_fit = fitted_params.get("alpha1", 0.08)
  a2_fit = fitted_params.get("alpha2", 0.045)
  
  # Constant PK/PD params
  es, er, ke, beta, gamma = 0.16, 0.015, 0.15, 0.25, 0.10
  h = 0.5
  duration = 90
  steps = int(duration / h)
  
  SS_init = 80.0 if patient.patient_id == 'patient-a' else 70.0
  SR_init = 2.0 if patient.patient_id == 'patient-a' else 10.0
  
  trajectories = []
  
  for _ in range(samples):
    # Sample from Gaussian priors (10% standard deviation)
    K_sample = np.random.normal(K_fit, 0.05 * K_fit)
    a1_sample = np.random.normal(a1_fit, 0.05 * a1_fit)
    a2_sample = np.random.normal(a2_fit, 0.05 * a2_fit)
    
    state = [SS_init, SR_init, 0.0, 0.0]
    t = 0.0
    vols = [state[0] + state[1]]
    
    for step in range(1, steps + 1):
      day = step * h
      dose = 10.0 if (int(day) % 7 == 0) else 0.0
      state = rk4_step(
        system_derivatives, t, state, h,
        a1_sample, a2_sample, K_sample, es, er, ke, beta, gamma, dose
      )
      t = day
      if int(day) == day:
        vols.append(state[0] + state[1])
        
    trajectories.append(vols)
    
  # Compute percentiles at each integer day
  trajectories = np.array(trajectories)
  lower_bound = np.percentile(trajectories, 5, axis=0)
  upper_bound = np.percentile(trajectories, 95, axis=0)
  median_curve = np.percentile(trajectories, 50, axis=0)
  
  timeline_uncertainty = []
  for idx, day in enumerate(range(0, duration + 1)):
    timeline_uncertainty.append({
      "day": day,
      "lower": round(float(lower_bound[idx]), 3),
      "median": round(float(median_curve[idx]), 3),
      "upper": round(float(upper_bound[idx]), 3)
    })
    
  return timeline_uncertainty
