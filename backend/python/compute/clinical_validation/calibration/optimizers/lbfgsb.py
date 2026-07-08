from scipy.optimize import minimize
from backend.python.compute.clinical_validation.calibration.optimizers.base import BaseOptimizer

class LBFGSBOptimizer(BaseOptimizer):
  """
  SciPy-backed L-BFGS-B bounded solver.
  """
  def __init__(self):
    super().__init__("L-BFGS-B")

  def minimize(self, cost_func, initial_guess, bounds):
    result = minimize(cost_func, initial_guess, method="L-BFGS-B", bounds=bounds)
    return {
      "success": result.success,
      "x": result.x.tolist(),
      "message": result.message,
      "fun": float(result.fun)
    }
