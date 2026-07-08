# Core Trajectory Simulator Coordinator
from backend.python.compute.simulation.solvers.rk4 import rk4_step
from backend.python.compute.common.models.simulation import SimulationResult

def system_derivatives(t, y, alpha1, alpha2, K, ES, ER, ke, beta, gamma, dose):
  """
  Calculates continuous-time derivative vectors:
  y = [sensitive, resistant, concentration, toxicity]
  """
  SS = y[0]
  SR = y[1]
  d = y[2]
  T = y[3]
  total = SS + SR

  # Competitive Lotka-Volterra growth
  dSS = alpha1 * SS * (1.0 - total / K) - d * ES * SS
  dSR = alpha2 * SR * (1.0 - total / K) - d * ER * SR

  # PK clearing
  dd = dose - ke * d

  # PD Toxicity accumulation
  dT = beta * d - gamma * T

  return [dSS, dSR, dd, dT]

def simulate_trajectory(patient, strategy, control_params):
  """
  Runs a daily step trajectory projection.
  """
  # Patient initial setup
  SS_init = 80.0 if patient.patient_id == 'patient-a' else 65.0 if patient.patient_id == 'patient-b' else 70.0
  SR_init = 2.0 if patient.patient_id == 'patient-a' else 15.0 if patient.patient_id == 'patient-b' else 10.0

  if control_params.get('initialResistantRatio') is not None:
    total_vol = SS_init + SR_init
    SR_init = total_vol * (float(control_params['initialResistantRatio']) / 100.0)
    SS_init = total_vol - SR_init

  y = [SS_init, SR_init, 0.0, 0.0]
  V0 = SS_init + SR_init
  progression_threshold = V0 * 1.2

  duration = int(control_params.get('duration', 180))
  mtd_dose = float(control_params.get('mtdDose', 10.0))
  interval = int(control_params.get('dosingInterval', 7))

  # Resolve parameter coefficients
  a1 = float(control_params.get('alpha1', 0.08 if patient.patient_id == 'patient-a' else 0.06 if patient.patient_id == 'patient-b' else 0.07))
  a2 = float(control_params.get('alpha2', 0.045 if patient.patient_id == 'patient-a' else 0.035 if patient.patient_id == 'patient-b' else 0.04))
  K_val = float(control_params.get('K', 200.0 if patient.patient_id == 'patient-a' else 150.0 if patient.patient_id == 'patient-b' else 180.0))
  es = float(control_params.get('ES', 0.16 if patient.patient_id == 'patient-a' else 0.12 if patient.patient_id == 'patient-b' else 0.10))
  er = float(control_params.get('ER', 0.015 if patient.patient_id == 'patient-a' else 0.01 if patient.patient_id == 'patient-b' else 0.015))
  
  ke = float(control_params.get('ke', 0.15))
  beta = float(control_params.get('beta', 0.25))
  gamma = float(control_params.get('gamma', 0.10))

  h = 0.5
  steps = int(duration / h)

  timeline = []
  cumulative_dose = 0.0
  time_to_progression = duration
  active_therapy = True

  # Loop step-by-step
  for step in range(steps + 1):
    t = step * h
    total_vol = y[0] + y[1]

    # Calculate active dose for this step based on selected strategy
    current_dose = 0.0
    # Dosing day criteria: t is integer multiple of interval
    is_dosing_day = (int(t) % interval == 0) and (t - int(t) == 0.0)

    if strategy.lower() == 'mtd':
      current_dose = mtd_dose if is_dosing_day else 0.0
    elif strategy.lower() == 'metronomic':
      current_dose = mtd_dose * 0.25 * h
    elif strategy.lower() == 'adaptive':
      if active_therapy and total_vol < 0.5 * V0:
        active_therapy = False
      elif not active_therapy and total_vol > 1.0 * V0:
        active_therapy = True
      
      if active_therapy:
        current_dose = mtd_dose if is_dosing_day else 0.0
      else:
        current_dose = 0.0

    cumulative_dose += current_dose

    if time_to_progression == duration and total_vol > progression_threshold and t > 10:
      time_to_progression = t

    timeline.append({
      "day": t,
      "sensitive": round(y[0], 4),
      "resistant": round(y[1], 4),
      "totalVolume": round(total_vol, 4),
      "drugConcentration": round(y[2], 5),
      "toxicity": round(y[3], 4),
      "dose": current_dose
    })

    # Perform RK4 step integration
    y = rk4_step(system_derivatives, t, y, h, a1, a2, K_val, es, er, ke, beta, gamma, current_dose)

  return SimulationResult(
    timeline=timeline,
    time_to_progression=time_to_progression,
    max_toxicity=round(max(pt["toxicity"] for pt in timeline), 2),
    cumulative_dose=round(cumulative_dose, 2)
  )
