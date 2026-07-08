class ParameterRegistry:
  """
  Main registry tracking biological simulation parameters, bounds, and guesses.
  """
  PARAMS = {
    "K": {
      "symbol": "K",
      "name": "Carrying Capacity",
      "bounds": (100.0, 300.0),
      "initial": 200.0,
      "citation": "Gatenby et al., Cancer Research 2009"
    },
    "alpha1": {
      "symbol": "a1",
      "name": "Sensitive Growth Rate",
      "bounds": (0.01, 0.20),
      "initial": 0.08,
      "citation": "Lotka-Volterra competition model"
    },
    "alpha2": {
      "symbol": "a2",
      "name": "Resistant Growth Rate",
      "bounds": (0.005, 0.10),
      "initial": 0.045,
      "citation": "Darwinian competitive cost model"
    },
    "ES": {
      "symbol": "es",
      "name": "Sensitive Drug Kill Rate",
      "bounds": (0.05, 0.50),
      "initial": 0.16,
      "citation": "Pharmacodynamic Efficacy Model"
    },
    "ER": {
      "symbol": "er",
      "name": "Resistant Drug Kill Rate",
      "bounds": (0.001, 0.05),
      "initial": 0.015,
      "citation": "Acquired clonal resistance indices"
    }
  }

  @classmethod
  def get_bounds(cls, keys):
    return [cls.PARAMS[k]["bounds"] for k in keys]

  @classmethod
  def get_initials(cls, keys):
    return [cls.PARAMS[k]["initial"] for k in keys]
