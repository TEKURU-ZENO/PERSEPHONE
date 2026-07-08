# Lotka-Volterra Competitive Suppression Differential Equations
from shared.math.constants import K

def lotka_volterra_derivatives(t, y, alpha1, alpha2, ES, ER, dose):
  """
  Computes derivatives [dS, dR] under Gatenby competitive models.
  y = [S, R] where S is sensitive, R is resistant volume.
  """
  S = max(0.0, y[0])
  R = max(0.0, y[1])
  total = S + R

  # Standard Lotka-Volterra competition derivatives
  dS = S * alpha1 * (1.0 - total / K) - ES * dose * S
  dR = R * alpha2 * (1.0 - total / K) - ER * dose * R

  return [dS, dR]
