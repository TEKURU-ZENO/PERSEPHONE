"""
Counterfactual Research Platform package for PERSEPHONE.
Provides synthetic cohort generation, multi-arm regimen space matrix,
mechanistic counterfactual simulation, comparative outcomes, and uncertainty quantification.
"""
from backend.python.compute.counterfactual.cohort import CohortMember, SyntheticCohort
from backend.python.compute.counterfactual.generator import SyntheticCohortGenerator
from backend.python.compute.counterfactual.treatment_matrix import TreatmentMatrix
from backend.python.compute.counterfactual.scenario import CounterfactualScenario
from backend.python.compute.counterfactual.simulator import CounterfactualSimulator
from backend.python.compute.counterfactual.outcomes import CounterfactualOutcomes
from backend.python.compute.counterfactual.uncertainty import CounterfactualUncertaintyEngine
from backend.python.compute.counterfactual.provenance import ScenarioProvenanceEngine, CausalProvenanceEngine
from backend.python.compute.counterfactual.comparison import CounterfactualComparator
from backend.python.compute.counterfactual.registry import CounterfactualRegistry

__all__ = [
    "CohortMember",
    "SyntheticCohort",
    "SyntheticCohortGenerator",
    "TreatmentMatrix",
    "CounterfactualScenario",
    "CounterfactualSimulator",
    "CounterfactualOutcomes",
    "CounterfactualUncertaintyEngine",
    "ScenarioProvenanceEngine",
    "CausalProvenanceEngine",
    "CounterfactualComparator",
    "CounterfactualRegistry"
]
