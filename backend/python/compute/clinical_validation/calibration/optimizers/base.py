class BaseOptimizer:
  """
  Abstract class defining interfaces for parameter estimation fitters.
  """
  def __init__(self, name):
    self.name = name

  def minimize(self, cost_func, initial_guess, bounds):
    """
    Minimizes the objective cost function using bounds and initial guesses.
    """
    raise NotImplementedError
