from backend.python.compute.optimization.evaluation.comparison import run_policy_comparison
from backend.python.compute.optimization.evaluation.report import generate_optimization_report

def execute_benchmark_suite(patient, control_params=None):
  """
  Runs all baseline and RL optimization policies, returning comparison outputs and markdown reports.
  """
  comparison = run_policy_comparison(patient, control_params)
  report = generate_optimization_report(comparison)
  
  return {
    "comparison": comparison,
    "markdownReport": report
  }
