import numpy as np
from backend.python.compute.simulation.solvers.rk4 import rk4_step
from backend.python.compute.simulation.core.simulator import system_derivatives
from backend.python.compute.optimization.environment.observation import build_observation
from backend.python.compute.optimization.environment.action_space import get_action_dose
from backend.python.compute.optimization.environment.reward.composite import CompositeReward
from backend.python.compute.optimization.environment.constraints.validator import SafetyConstraintValidator

from backend.python.compute.simulation.params import get_default_model_params

class TumorEvolutionEnv:
  """
  Oncology simulation environment conforming to OpenAI Gym step transitions.
  """
  def __init__(self, patient, control_params=None):
    self.patient = patient
    self.control_params = control_params or {}
    defaults = get_default_model_params()
    p_params = patient.model_params if hasattr(patient, 'model_params') and patient.model_params else {}
    if not isinstance(p_params, dict):
      p_params = {}
    
    # Base coefficients from model_params or central defaults
    self.a1 = float(self.control_params.get('alpha1', p_params.get('alpha1', defaults['alpha1'])))
    self.a2 = float(self.control_params.get('alpha2', p_params.get('alpha2', defaults['alpha2'])))
    self.K_val = float(self.control_params.get('K', p_params.get('K', defaults['K'])))
    self.es = float(self.control_params.get('ES', p_params.get('ES', defaults['ES'])))
    self.er = float(self.control_params.get('ER', p_params.get('ER', defaults['ER'])))
    self.ke = float(self.control_params.get('ke', p_params.get('ke', defaults['ke'])))
    self.beta = float(self.control_params.get('beta', p_params.get('beta', defaults['beta'])))
    self.gamma = float(self.control_params.get('gamma', p_params.get('gamma', defaults['gamma'])))
    self.aSR = float(self.control_params.get('aSR', p_params.get('aSR', defaults.get('aSR', 1.0))))
    self.aRS = float(self.control_params.get('aRS', p_params.get('aRS', defaults.get('aRS', 1.0))))

    self.duration = int(self.control_params.get('duration', 180))
    self.h = 0.5
    self.max_steps = int(self.duration / self.h)
    
    # Establish initial volumes
    self.SS_init = float(self.control_params.get('SS_init', p_params.get('SS_init', 80.0)))
    self.SR_init = float(self.control_params.get('SR_init', p_params.get('SR_init', 2.0)))
    self.V0 = self.SS_init + self.SR_init
    self.progression_threshold = self.V0 * 1.2

    self.reset()

  def reset(self):
    self.step_idx = 0
    self.t = 0.0
    self.state = [self.SS_init, self.SR_init, 0.0, 0.0] # [SS, SR, drug, toxicity]
    return self._get_obs()

  def _get_obs(self):
    return build_observation(
      self.state[0],
      self.state[1],
      self.state[2],
      self.state[3],
      self.step_idx,
      self.max_steps
    )

  def step(self, action_idx):
    # Map index to dose level
    raw_dose = get_action_dose(action_idx, mtd_dose=10.0)

    # Apply Clinical Safety Constraint Filter
    safety_check = SafetyConstraintValidator.validate_action(
      self.state[3], # current toxicity
      self.patient.clinical_metrics,
      raw_dose
    )

    actual_dose = raw_dose
    safety_override = False
    if not safety_check["valid"]:
      # Override dose to 0.0 for safety holiday
      actual_dose = 0.0
      safety_override = True

    # Integrate step using Runge-Kutta 4th order (RK4)
    # The derivatives solve competitive growth + PK + PD together
    self.state = rk4_step(
      system_derivatives, 
      self.t, 
      self.state, 
      self.h, 
      self.a1, self.a2, self.K_val, self.es, self.er, self.ke, self.beta, self.gamma, 
      actual_dose
    )

    self.step_idx += 1
    self.t = self.step_idx * self.h

    total_vol = self.state[0] + self.state[1]
    is_alive = total_vol < self.progression_threshold

    # Calculate step rewards
    reward = CompositeReward.calculate(total_vol, self.state[3], is_alive, actual_dose > 0.0)
    
    if not is_alive:
      reward -= 50.0 # Terminal progression penalty

    terminated = not is_alive or self.step_idx >= self.max_steps
    
    info = {
      "day": self.t,
      "actualDose": actual_dose,
      "safetyOverride": safety_override,
      "violations": safety_check["violations"]
    }

    return self._get_obs(), reward, terminated, info
