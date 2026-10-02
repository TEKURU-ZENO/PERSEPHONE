"""
Knowledge subpackage for PERSEPHONE Research Intelligence Platform.
"""
from backend.python.compute.research_intelligence.knowledge.hypothesis import ClinicalHypothesisGenerator
from backend.python.compute.research_intelligence.knowledge.contradiction import ContradictionDetector

__all__ = ["ClinicalHypothesisGenerator", "ContradictionDetector"]
