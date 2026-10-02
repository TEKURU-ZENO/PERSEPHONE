"""
Factuality Verification Module for PERSEPHONE Governance Platform.
Cross-verifies claims, clinical trial endpoints, and efficacy statements against
authoritative GroundingGate evidence items and reference datasets.
"""
from typing import Dict, List, Any, Optional


class FactualityVerifier:
    """
    Verifies that clinical claims asserted by models or agents reflect empirical clinical data
    without numerical inversion, fabricated endpoints, or hallucinated registrational trials.
    """

    @classmethod
    def verify_factuality(
        cls,
        claims: List[Dict[str, Any]],
        verified_evidence: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        verified_evidence = verified_evidence or []
        verified_pmids = set(str(e.get("pmid")) for e in verified_evidence if e.get("pmid"))

        audited_claims = []
        factual_violations = []

        for c in claims:
            cid = c.get("claim_id", "CLM-UNKNOWN")
            statement = str(c.get("statement", c.get("assertion", "")))
            grounding_status = c.get("grounding_status", "UNVERIFIED")

            is_factual = True
            flags = []

            # 1. Grounding check
            if grounding_status == "UNGROUNDED":
                is_factual = False
                flags.append("UNGROUNDED_ASSERTION: Claim lacks backing registrational citation or empirical proof.")

            # 2. Inversion check (e.g. HR > 1.0 claiming survival benefit)
            hr = c.get("hazard_ratio")
            if isinstance(hr, (int, float)) and hr >= 1.0 and ("benefit" in statement.lower() or "superior" in statement.lower()):
                is_factual = False
                flags.append(f"INVERTED_METRIC: Hazard ratio {hr} >= 1.0 contradicts assertion of therapeutic survival benefit.")

            # 3. Fabricated trial check
            cited_pmid = c.get("pmid")
            if cited_pmid and verified_pmids and str(cited_pmid) not in verified_pmids:
                flags.append(f"UNRECOGNIZED_CITATION: PMID {cited_pmid} not recognized in vetted registrational corpus.")

            if not is_factual or flags:
                factual_violations.append({
                    "claim_id": cid,
                    "statement": statement,
                    "flags": flags
                })

            audited_claims.append({
                "claim_id": cid,
                "factual": is_factual and len(flags) == 0,
                "grounding_status": grounding_status,
                "flags": flags
            })

        passed = len(factual_violations) == 0
        return {
            "passed_factuality": passed,
            "factuality_score": round((len(audited_claims) - len(factual_violations)) / max(1, len(audited_claims)), 3),
            "total_claims_audited": len(audited_claims),
            "factual_violations_count": len(factual_violations),
            "violations": factual_violations,
            "audited_claims": audited_claims
        }
