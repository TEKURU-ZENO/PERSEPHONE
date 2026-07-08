from backend.python.compute.simulation.core.simulator import simulate_trajectory

class SimulationSolverSkill:
  """
  Skill executing mechanistical RK4 tumor projections.
  """
  @staticmethod
  def run_simulation(patient_twin, strategy="mtd", params=None):
    control_params = params or {
      "mtdDose": 10,
      "dosingInterval": 7,
      "initialResistantRatio": 2.4,
      "duration": 180
    }
    return simulate_trajectory(patient_twin, strategy, control_params)
