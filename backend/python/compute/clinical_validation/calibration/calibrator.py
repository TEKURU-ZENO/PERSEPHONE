import numpy as np
from backend.python.compute.simulation.solvers.rk4 import rk4_step
from backend.python.compute.simulation.core.simulator import system_derivatives
from backend.python.compute.clinical_validation.calibration.optimizers.lbfgsb import LBFGSBOptimizer
from backend.python.compute.clinical_validation.parameters.registry import ParameterRegistry

def evaluate_sim_mse(params, days, true_vols, patient):
  """
  Integrates RK4 steps and sums squared errors between simulated total volumes and true volumes.
  """
  K_val, a1, a2 = params
  
  # Constant PK/PD clearances
  es, er, ke, beta, gamma = 0.16, 0.015, 0.15, 0.25, 0.10
  h = 0.5
  
  # Reset state [SS, SR, drug, toxicity]
  SS_init = 80.0 if patient.patient_id == 'patient-a' else 70.0
  SR_init = 2.0 if patient.patient_id == 'patient-a' else 10.0
  state = [SS_init, SR_init, 0.0, 0.0]
  
  # Standard MTD weekly dosing schedule
  simulated_vols = {}
  t = 0.0
  max_day = max(days)
  steps = int(max_day / h)
  
  # Map t=0 volume
  simulated_vols[0.0] = state[0] + state[1]

  for step in range(1, steps + 1):
    day = step * h
    dose = 10.0 if (int(day) % 7 == 0) else 0.0
    state = rk4_step(
      system_derivatives, t, state, h,
      a1, a2, K_val, es, er, ke, beta, gamma, dose
    )
    t = day
    
    # Store at integer days matching empirical datasets
    if int(day) == day:
      simulated_vols[int(day)] = state[0] + state[1]

  # Sum squared errors
  sse = 0.0
  for d, true_val in zip(days, true_vols):
    sim_val = simulated_vols.get(d, simulated_vols[max(simulated_vols.keys())])
    sse += (sim_val - true_val) ** 2
    
  return sse / len(days)

def fit_patient_parameters(patient, empirical_data):
  """
  Estimates personalized biological values from observed clinical metrics.
  """
  days = [pt["day"] for pt in empirical_data]
  true_vols = [pt["volume"] for pt in empirical_data]

  param_keys = ["K", "alpha1", "alpha2"]
  bounds = ParameterRegistry.get_bounds(param_keys)
  initials = ParameterRegistry.get_initials(param_keys)

  # Setup objective function wrapper
  cost_func = lambda p: evaluate_sim_mse(p, days, true_vols, patient)

  optimizer = LBFGSBOptimizer()
  fit_res = optimizer.minimize(cost_func, initials, bounds)

  fit_params = fit_res["x"]
  
  return {
    "success": fit_res["success"],
    "calibratedParams": {
      "K": round(fit_params[0], 2),
      "alpha1": round(fit_params[1], 4),
      "alpha2": round(fit_params[2], 4)
    },
    "mse": round(fit_res["fun"], 4)
  }
