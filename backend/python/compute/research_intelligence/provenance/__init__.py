"""
Provenance subpackage for PERSEPHONE Research Intelligence Platform.
"""
from backend.python.compute.research_intelligence.provenance.source import ProvenanceSource
from backend.python.compute.research_intelligence.provenance.evidence_item import EvidenceItem
from backend.python.compute.research_intelligence.provenance.claim import ClinicalClaim
from backend.python.compute.research_intelligence.provenance.snapshot import EvidenceSnapshot
from backend.python.compute.research_intelligence.provenance.verifier import EvidenceVerifier
from backend.python.compute.research_intelligence.provenance.grounding import GroundingGate
from backend.python.compute.research_intelligence.provenance.lineage import EvidenceLineageTracker

__all__ = [
    "ProvenanceSource",
    "EvidenceItem",
    "ClinicalClaim",
    "EvidenceSnapshot",
    "EvidenceVerifier",
    "GroundingGate",
    "EvidenceLineageTracker"
]
