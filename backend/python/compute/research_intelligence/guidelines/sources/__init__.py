"""
Guideline sources subpackage.
"""
from backend.python.compute.research_intelligence.guidelines.sources.nccn import NCCN_DECISION_RULES
from backend.python.compute.research_intelligence.guidelines.sources.asco import ASCO_DECISION_RULES
from backend.python.compute.research_intelligence.guidelines.sources.esmo import ESMO_DECISION_RULES

ALL_GUIDELINE_RULES = NCCN_DECISION_RULES + ASCO_DECISION_RULES + ESMO_DECISION_RULES

__all__ = ["NCCN_DECISION_RULES", "ASCO_DECISION_RULES", "ESMO_DECISION_RULES", "ALL_GUIDELINE_RULES"]
