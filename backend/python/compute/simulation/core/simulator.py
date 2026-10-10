# Core Trajectory Simulator Coordinator
from backend.python.compute.simulation.solvers.rk4 import rk4_step
from backend.python.compute.common.models.simulation import SimulationResult
from backend.python.compute.simulation.params import get_default_model_params

def system_derivatives(t, y, alpha1, alpha2, K, ES, ER, ke, beta, gamma, dose, aSR=1.0, aRS=1.0):
  """
  Calculates continuous-time derivative vectors:
  y = [sensitive, resistant, concentration, toxicity]
  """
  SS = y[0]
  SR = y[1]
  d = y[2]
  T = y[3]

  # Competitive Lotka-Volterra growth with cross-competition
  dSS = alpha1 * SS * (1.0 - (SS + aSR * SR) / K) - d * ES * SS
  dSR = alpha2 * SR * (1.0 - (SR + aRS * SS) / K) - d * ER * SR

  # PK clearing
  dd = dose - ke * d

  # PD Toxicity accumulation
  dT = beta * d - gamma * T

  return [dSS, dSR, dd, dT]

def simulate_trajectory(patient, strategy, control_params):
  """
  Runs a daily step trajectory projection.
  """
  defaults = get_default_model_params()
  p_params = patient.model_params if hasattr(patient, 'model_params') and patient.model_params else {}
  if not isinstance(p_params, dict):
    p_params = {}

  # Patient initial setup
  SS_init = float(control_params.get('SS_init', p_params.get('SS_init', 80.0)))
  SR_init = float(control_params.get('SR_init', p_params.get('SR_init', 2.0)))

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

  # Resolve parameter coefficients without hardcoded patient ID ternaries
  a1 = float(control_params.get('alpha1', p_params.get('alpha1', defaults['alpha1'])))
  a2 = float(control_params.get('alpha2', p_params.get('alpha2', defaults['alpha2'])))
  K_val = float(control_params.get('K', p_params.get('K', defaults['K'])))
  es = float(control_params.get('ES', p_params.get('ES', defaults['ES'])))
  er = float(control_params.get('ER', p_params.get('ER', defaults['ER'])))
  ke = float(control_params.get('ke', p_params.get('ke', defaults['ke'])))
  beta = float(control_params.get('beta', p_params.get('beta', defaults['beta'])))
  gamma = float(control_params.get('gamma', p_params.get('gamma', defaults['gamma'])))
  aSR = float(control_params.get('aSR', p_params.get('aSR', defaults.get('aSR', 1.0))))
  aRS = float(control_params.get('aRS', p_params.get('aRS', defaults.get('aRS', 1.0))))

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
      "sensitive": y[0],
      "resistant": y[1],
      "totalVolume": total_vol,
      "drugConcentration": y[2],
      "toxicity": y[3],
      "dose": current_dose
    })

    # Perform RK4 step integration
    y = rk4_step(system_derivatives, t, y, h, a1, a2, K_val, es, er, ke, beta, gamma, current_dose, aSR, aRS)

  return SimulationResult(
    timeline=timeline,
    time_to_progression=time_to_progression,
    max_toxicity=round(max(pt["toxicity"] for pt in timeline), 2),
    cumulative_dose=round(cumulative_dose, 2)
  )
