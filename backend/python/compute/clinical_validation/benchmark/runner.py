def execute_validation_benchmarks(fitted_params):
  """
  Compares fitted parameters against Gatenby 2009 published clinical trials parameters.
  """
  literature_ref = {
    "K": 200.0,
    "alpha1": 0.08,
    "alpha2": 0.04
  }
  
  errors = {
    "K": abs(fitted_params.get("K", 200.0) - literature_ref["K"]),
    "alpha1": abs(fitted_params.get("alpha1", 0.08) - literature_ref["alpha1"]),
    "alpha2": abs(fitted_params.get("alpha2", 0.045) - literature_ref["alpha2"])
  }
  
  return {
    "literatureRef": literature_ref,
    "absoluteDeltas": errors
  }
