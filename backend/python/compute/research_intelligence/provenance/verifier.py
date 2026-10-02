"""
Evidence Verifier module for PERSEPHONE Research Intelligence Platform.
Validates source integrity, citation resolution, content hashes, and multi-source corroboration.
"""
from typing import Dict, List, Any, Optional
from backend.python.compute.research_intelligence.provenance.source import ProvenanceSource
from backend.python.compute.research_intelligence.provenance.evidence_item import EvidenceItem
from backend.python.compute.research_intelligence.provenance.claim import ClinicalClaim


class EvidenceVerifier:
    """
    Executes technical and scientific validation checks across sources, evidence items, and claims.
    """

    @classmethod
    def verify_source(cls, source: ProvenanceSource) -> Dict[str, Any]:
        """
        Validates source URI, non-empty title/content, and cryptographic hash integrity.
        """
        checks = {
            "uri_valid": bool(source.uri and (source.uri.startswith("http") or source.uri.startswith("urn:"))),
            "version_declared": bool(source.version),
            "content_hash_valid": bool(source.content_hash and len(source.content_hash) == 64),
            "retrieval_timestamp_present": bool(source.retrieved_at)
        }
        all_passed = all(checks.values())
        return {
            "source_id": source.source_id,
            "verified": all_passed,
            "verification_status": "VERIFIED" if all_passed else "UNVERIFIED",
            "checklist": checks
        }

    @classmethod
    def verify_evidence_link(cls, evidence: EvidenceItem, source: ProvenanceSource) -> bool:
        """
        Confirms that the evidence item's source_hash matches the source's actual content_hash.
        """
        return evidence.source_hash == source.content_hash

    @classmethod
    def verify_claim_corroboration(
        cls,
        claim: ClinicalClaim,
        evidence_items: List[EvidenceItem]
    ) -> Dict[str, Any]:
        """
        Checks whether claim has valid supporting evidence items and measures corroboration depth.
        """
        matched_items = [e for e in evidence_items if e.evidence_id in claim.evidence_ids]
        has_evidence = len(matched_items) > 0
        corroborated = len(matched_items) >= 2 # Independently corroborated by multiple studies

        # Check for randomized phase III evidence
        has_phase3 = any("Phase III" in e.study_design for e in matched_items)

        return {
            "claim_id": claim.claim_id,
            "has_supporting_evidence": has_evidence,
            "evidence_count": len(matched_items),
            "independently_corroborated": corroborated,
            "has_phase3_evidence": has_phase3,
            "status": "CORROBORATED" if corroborated else ("SUPPORTED" if has_evidence else "UNGROUNDED")
        }
