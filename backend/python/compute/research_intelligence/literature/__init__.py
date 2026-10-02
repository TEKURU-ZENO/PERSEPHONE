"""
Literature subpackage for PERSEPHONE Research Intelligence Platform.
"""
from backend.python.compute.research_intelligence.literature.citation import CitationManager
from backend.python.compute.research_intelligence.literature.evidence import EvidenceExtractor
from backend.python.compute.research_intelligence.literature.retrieval import LiteratureRetriever

__all__ = ["CitationManager", "EvidenceExtractor", "LiteratureRetriever"]
