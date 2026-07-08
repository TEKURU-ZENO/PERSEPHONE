from backend.python.compute.optimization.benchmark.runner import execute_benchmark_suite

class OptimizationPolicySkill:
  """
  Skill executing trained policy benchmarks and rewards calculations.
  """
  @staticmethod
  def benchmark_policies(patient_twin):
    return execute_benchmark_suite(patient_twin)
