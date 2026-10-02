"""
Research Intelligence Platform package for PERSEPHONE.
Provides ClinicalEvidenceGraph, Literature Retrieval, Versioned Guidelines,
Bidirectional Trial Linking, Contradiction Detection, Epistemic Grounding, and Merkle Lineage Provenance.
"""
from backend.python.compute.research_intelligence.graph.evidence_graph import ClinicalEvidenceGraph, EvidenceNode, EvidenceEdge
from backend.python.compute.research_intelligence.graph.traverser import EvidenceGraphTraverser
from backend.python.compute.research_intelligence.literature.retrieval import LiteratureRetriever
from backend.python.compute.research_intelligence.literature.citation import CitationManager
from backend.python.compute.research_intelligence.literature.evidence import EvidenceExtractor
from backend.python.compute.research_intelligence.guidelines.recommendation import GuidelineRecommender
from backend.python.compute.research_intelligence.trials.evidence_linker import TrialEvidenceLinker
from backend.python.compute.research_intelligence.knowledge.hypothesis import ClinicalHypothesisGenerator
from backend.python.compute.research_intelligence.knowledge.contradiction import ContradictionDetector
from backend.python.compute.research_intelligence.provenance.source import ProvenanceSource
from backend.python.compute.research_intelligence.provenance.evidence_item import EvidenceItem
from backend.python.compute.research_intelligence.provenance.claim import ClinicalClaim
from backend.python.compute.research_intelligence.provenance.snapshot import EvidenceSnapshot
from backend.python.compute.research_intelligence.provenance.verifier import EvidenceVerifier
from backend.python.compute.research_intelligence.provenance.grounding import GroundingGate
from backend.python.compute.research_intelligence.provenance.lineage import EvidenceLineageTracker
from backend.python.compute.research_intelligence.registry import ResearchIntelligenceRegistry

__all__ = [
    "ClinicalEvidenceGraph",
    "EvidenceNode",
    "EvidenceEdge",
    "EvidenceGraphTraverser",
    "LiteratureRetriever",
    "CitationManager",
    "EvidenceExtractor",
    "GuidelineRecommender",
    "TrialEvidenceLinker",
    "ClinicalHypothesisGenerator",
    "ContradictionDetector",
    "ProvenanceSource",
    "EvidenceItem",
    "ClinicalClaim",
    "EvidenceSnapshot",
    "EvidenceVerifier",
    "GroundingGate",
    "EvidenceLineageTracker",
    "ResearchIntelligenceRegistry"
]
