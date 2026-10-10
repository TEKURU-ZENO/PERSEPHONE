# Lotka-Volterra Competitive Suppression Differential Equations
from backend.python.compute.simulation.params import get_default_model_params

_defaults = get_default_model_params()
K_DEFAULT = _defaults.get("K", 200.0)

def lotka_volterra_derivatives(t, y, alpha1, alpha2, ES, ER, dose, K=None, aSR=1.0, aRS=1.0):
  """
  Computes derivatives [dS, dR] under Gatenby competitive models.
  y = [S, R] where S is sensitive, R is resistant volume.
  """
  S = max(0.0, y[0])
  R = max(0.0, y[1])
  cap = K if K is not None else K_DEFAULT

  # Standard Lotka-Volterra competition derivatives
  dS = S * alpha1 * (1.0 - (S + aSR * R) / cap) - ES * dose * S
  dR = R * alpha2 * (1.0 - (R + aRS * S) / cap) - ER * dose * R

  return [dS, dR]
