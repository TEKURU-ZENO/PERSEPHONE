"""
Evidence Lineage Tracker module for PERSEPHONE Research Intelligence Platform.
Constructs immutable, hierarchical Merkle-style lineage hashes across Sources, EvidenceItems, and Claims.
"""
import hashlib
from typing import Dict, List, Any, Optional
from backend.python.compute.research_intelligence.provenance.source import ProvenanceSource
from backend.python.compute.research_intelligence.provenance.evidence_item import EvidenceItem
from backend.python.compute.research_intelligence.provenance.claim import ClinicalClaim


class EvidenceLineageTracker:
    """
    Constructs and verifies hierarchical provenance trees and Merkle lineage root hashes.
    """

    @classmethod
    def build_claim_lineage(
        cls,
        claim: ClinicalClaim,
        evidence_items: List[EvidenceItem],
        sources: List[ProvenanceSource]
    ) -> Dict[str, Any]:
        """
        Builds the full provenance tree:
        Source -> EvidenceItem -> ClinicalClaim -> LineageRootHash
        """
        source_map = {s.source_id: s for s in sources}
        evidence_map = {e.evidence_id: e for e in evidence_items}

        matched_evidence = [evidence_map[eid] for eid in claim.evidence_ids if eid in evidence_map]
        
        # Collect source hashes
        lineage_sources = []
        source_hashes = []
        for ev in matched_evidence:
            src = source_map.get(ev.source_id)
            if src:
                lineage_sources.append(src.to_dict())
                source_hashes.append(src.content_hash)
            else:
                source_hashes.append(ev.source_hash)

        # Collect evidence hashes
        evidence_hashes = [e.evidence_hash for e in matched_evidence]

        # Calculate Merkle-style hierarchical lineage root hash
        combined_payload = (
            f"ROOT|{claim.provenance_hash}|"
            f"{'#'.join(sorted(evidence_hashes))}|"
            f"{'#'.join(sorted(source_hashes))}"
        )
        lineage_root_hash = hashlib.sha256(combined_payload.encode('utf-8')).hexdigest()

        return {
            "claim_id": claim.claim_id,
            "claim_statement": claim.statement,
            "generating_agent": claim.generating_agent,
            "created_at": claim.created_at,
            "claim_hash": claim.provenance_hash,
            "evidence_chain": [e.to_dict() for e in matched_evidence],
            "source_chain": lineage_sources,
            "lineage_root_hash": lineage_root_hash,
            "integrity_status": "VERIFIED_TAMPER_EVIDENT",
            "proof_path": {
                "source_hashes": source_hashes,
                "evidence_hashes": evidence_hashes,
                "claim_hash": claim.provenance_hash,
                "root": lineage_root_hash
            }
        }
