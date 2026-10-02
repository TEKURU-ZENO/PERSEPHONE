"""
Grounding Gate module for PERSEPHONE Research Intelligence Platform.
Enforces strict epistemic gating: evaluates claims for supporting evidence, provenance completeness,
and quality, blocking ungrounded assertions from clinical presentation.
"""
from typing import Dict, List, Any, Optional
from backend.python.compute.research_intelligence.provenance.claim import ClinicalClaim
from backend.python.compute.research_intelligence.provenance.evidence_item import EvidenceItem
from backend.python.compute.research_intelligence.provenance.verifier import EvidenceVerifier


class GroundingGate:
    """
    Automated scientific quality and grounding gatekeeper.
    Refuses to permit ungrounded or contradicted claims to reach the tumor board recommendation report.
    """

    @classmethod
    def evaluate_claim(
        cls,
        claim: ClinicalClaim,
        available_evidence: List[EvidenceItem],
        contradictions: Optional[List[Dict[str, Any]]] = None,
        is_stale: bool = False
    ) -> Dict[str, Any]:
        """
        Executes gating checklist:
        Evidence Found? -> Source Verified? -> Provenance Complete? -> Quality Sufficient?
        """
        contradictions = contradictions or []
        corrob = EvidenceVerifier.verify_claim_corroboration(claim, available_evidence)

        # 1. Evidence required & found?
        if not corrob["has_supporting_evidence"]:
            return {
                "claim_id": claim.claim_id,
                "grounding_status": "UNGROUNDED",
                "allow_clinical_presentation": False,
                "confidence_adjustment": 0.0,
                "rationale": "BLOCK: Claim lacks any linked empirical scientific evidence or clinical trial proof."
            }

        # 2. Check for active severe contradictions
        critical_conflicts = [c for c in contradictions if c.get("severity") in ["CRITICAL", "HIGH"]]
        if critical_conflicts:
            return {
                "claim_id": claim.claim_id,
                "grounding_status": "CONTRADICTED",
                "allow_clinical_presentation": False,
                "confidence_adjustment": 0.25,
                "rationale": f"FLAG: Contradicted by {len(critical_conflicts)} clinical discordances (e.g. {critical_conflicts[0].get('statement', '')})."
            }

        # 3. Check for staleness
        if is_stale:
            return {
                "claim_id": claim.claim_id,
                "grounding_status": "STALE",
                "allow_clinical_presentation": False,
                "confidence_adjustment": 0.40,
                "rationale": "FLAG: Supporting guideline or evidence has been superseded by a newer registrational standard."
            }

        # 4. Check for high-level verification vs partial verification
        matched_items = [e for e in available_evidence if e.evidence_id in claim.evidence_ids]
        has_high_quality = any(e.cebm_level in ["Level 1a", "Level 1b"] for e in matched_items)
        has_nccn_cat1 = any(e.nccn_category == "Category 1" for e in matched_items)

        if has_high_quality or (has_nccn_cat1 and corrob["independently_corroborated"]):
            status = "VERIFIED"
            allow = True
            conf_adj = 1.0
            rationale = "ALLOW: Claim supported by high-quality randomized evidence and verified provenance."
        else:
            status = "PARTIAL"
            allow = True
            conf_adj = 0.75
            rationale = "ALLOW WITH CAUTION: Claim supported by moderate or early-phase evidence; independent corroboration advised."

        return {
            "claim_id": claim.claim_id,
            "grounding_status": status,
            "allow_clinical_presentation": allow,
            "confidence_adjustment": conf_adj,
            "rationale": rationale,
            "corroboration_summary": corrob
        }
