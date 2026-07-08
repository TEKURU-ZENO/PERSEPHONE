import threading

class BlackboardMemory:
  """
  Thread-safe central Blackboard Memory for multi-agent coordination.
  """
  def __init__(self):
    self._lock = threading.Lock()
    self._data = {
      "patient_twin": None,
      "tumor_evolution": None,
      "simulation_results": None,
      "therapy_plan": None,
      "optimization_results": None,
      "safety_audits": [],
      "kg_pathways": None,
      "grounded_evidence": None,
      "literature_evidence": None,
      "clinical_memory": None,
      "validation_scorecard": None,
      "explainability_rationale": None,
      "final_report": None,
      "agent_contributions": []
    }

  def write(self, key, value):
    with self._lock:
      if key in self._data:
        self._data[key] = value

  def read(self, key):
    with self._lock:
      return self._data.get(key)

  def add_contribution(self, agent_name, payload):
    with self._lock:
      self._data["agent_contributions"].append({
        "agent": agent_name,
        "payload": payload
      })

  def get_all_data(self):
    with self._lock:
      return self._data.copy()
