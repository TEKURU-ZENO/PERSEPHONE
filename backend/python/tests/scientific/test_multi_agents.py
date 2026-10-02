import unittest
from backend.python.compute.ai_runtime.agents.blackboard import BlackboardMemory
from backend.python.compute.ai_runtime.agents.bus import AgentEventBus
from backend.python.compute.ai_runtime.skills.simulation.solver import SimulationSolverSkill
from backend.python.compute.ai_runtime.agents.runtime import AgentCouncilRuntime

class TestClinicalMultiAgents(unittest.TestCase):
  def test_blackboard_read_write(self):
    bb = BlackboardMemory()
    bb.write("patient_twin", {"id": "patient-a", "name": "Elena"})
    data = bb.read("patient_twin")
    self.assertEqual(data["id"], "patient-a")

  def test_event_bus_publishing(self):
    bus = AgentEventBus()
    events_triggered = []
    bus.subscribe(lambda event_type, source, payload: events_triggered.append(event_type))
    bus.publish_event("PATIENT_UPDATED", "patient_twin")
    self.assertEqual(events_triggered[0], "PATIENT_UPDATED")

  def test_simulation_skill_exec(self):
    # Mock patient dict for simulation skill call
    class DummyPatient:
      def __init__(self):
        self.patient_id = "patient-a"
        self.name = "Elena"
        self.stage = "III"
        self.diagnosis = "Ovarian Cancer"
        
    p = DummyPatient()
    sim = SimulationSolverSkill.run_simulation(p, "mtd")
    self.assertTrue(sim.time_to_progression > 0)

  def test_agent_council_debate_execution(self):
    res = AgentCouncilRuntime.run_debate({"id": "patient-a", "variants": ["BRCA1"]})
    self.assertEqual(len(res["debateTranscript"]), 23) # 23 agents
    self.assertEqual(len(res["agentMetrics"]), 23)
    self.assertTrue(res["consensusStatus"] in ["online", "degraded", "offline", "abstained"])

if __name__ == '__main__':
  unittest.main()
