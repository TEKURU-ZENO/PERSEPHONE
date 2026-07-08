import numpy as np
from backend.python.compute.simulation.solvers.rk4 import rk4_step
from backend.python.compute.simulation.core.simulator import system_derivatives
from backend.python.compute.optimization.environment.observation import build_observation
from backend.python.compute.optimization.environment.action_space import get_action_dose
from backend.python.compute.optimization.environment.reward.composite import CompositeReward
from backend.python.compute.optimization.environment.constraints.validator import SafetyConstraintValidator

class TumorEvolutionEnv:
  """
  Oncology simulation environment conforming to OpenAI Gym step transitions.
  """
  def __init__(self, patient, control_params=None):
    self.patient = patient
    self.control_params = control_params or {}
    
    # Base coefficients
    self.a1 = float(self.control_params.get('alpha1', 0.08 if patient.patient_id == 'patient-a' else 0.06 if patient.patient_id == 'patient-b' else 0.07))
    self.a2 = float(self.control_params.get('alpha2', 0.045 if patient.patient_id == 'patient-a' else 0.035 if patient.patient_id == 'patient-b' else 0.04))
    self.K_val = float(self.control_params.get('K', 200.0 if patient.patient_id == 'patient-a' else 150.0 if patient.patient_id == 'patient-b' else 180.0))
    self.es = float(self.control_params.get('ES', 0.16 if patient.patient_id == 'patient-a' else 0.12 if patient.patient_id == 'patient-b' else 0.10))
    self.er = float(self.control_params.get('ER', 0.015 if patient.patient_id == 'patient-a' else 0.01 if patient.patient_id == 'patient-b' else 0.015))
    self.ke = float(self.control_params.get('ke', 0.15))
    self.beta = float(self.control_params.get('beta', 0.25))
    self.gamma = float(self.control_params.get('gamma', 0.10))

    self.duration = int(self.control_params.get('duration', 180))
    self.h = 0.5
    self.max_steps = int(self.duration / self.h)
    
    # Establish initial volumes
    self.SS_init = 80.0 if patient.patient_id == 'patient-a' else 65.0 if patient.patient_id == 'patient-b' else 70.0
    self.SR_init = 2.0 if patient.patient_id == 'patient-a' else 15.0 if patient.patient_id == 'patient-b' else 10.0
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
