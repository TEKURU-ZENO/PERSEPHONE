from backend.python.compute.ai_runtime.agents.instances.orchestrator import ChiefOrchestratorAgent
from backend.python.compute.ai_runtime.agents.instances.patient_twin import PatientTwinAgent
from backend.python.compute.ai_runtime.agents.instances.evolution import TumorEvolutionAgent
from backend.python.compute.ai_runtime.agents.instances.simulation import SimulationAgent
from backend.python.compute.ai_runtime.agents.instances.therapy import TherapyPlanningAgent
from backend.python.compute.ai_runtime.agents.instances.optimization import OptimizationAgent
from backend.python.compute.ai_runtime.agents.instances.safety import SafetyAgent
from backend.python.compute.ai_runtime.agents.instances.kg import KnowledgeGraphAgent
from backend.python.compute.ai_runtime.agents.instances.evidence import EvidenceAgent
from backend.python.compute.ai_runtime.agents.instances.graph_rag import GraphRAGAgent
from backend.python.compute.ai_runtime.agents.instances.memory import ClinicalMemoryAgent
from backend.python.compute.ai_runtime.agents.instances.validation import ValidationAgent
from backend.python.compute.ai_runtime.agents.instances.explainability import ExplainabilityAgent
from backend.python.compute.ai_runtime.agents.instances.report import ClinicalReportAgent

class AgentRegistry:
  """
  Registry managing instances of the 14 specialist agents.
  """
  _REGISTRY = {
    "orchestrator": ChiefOrchestratorAgent,
    "patient_twin": PatientTwinAgent,
    "evolution": TumorEvolutionAgent,
    "simulation": SimulationAgent,
    "therapy": TherapyPlanningAgent,
    "optimization": OptimizationAgent,
    "safety": SafetyAgent,
    "kg": KnowledgeGraphAgent,
    "evidence": EvidenceAgent,
    "graph_rag": GraphRAGAgent,
    "memory": ClinicalMemoryAgent,
    "validation": ValidationAgent,
    "explainability": ExplainabilityAgent,
    "report": ClinicalReportAgent
  }

  @classmethod
  def register_agent(cls, name, agent_class):
    cls._REGISTRY[name] = agent_class

  @classmethod
  def get_agent_class(cls, name):
    return cls._REGISTRY.get(name)

  @classmethod
  def list_registered_agents(cls):
    return list(cls._REGISTRY.keys())
