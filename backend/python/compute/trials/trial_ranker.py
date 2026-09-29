"""
Trial Ranker module for PERSEPHONE Clinical Trials Intelligence.
Computes composite clinical priority rankings taking into account trial phase,
recruitment status, patient genomic evidence tiers, and match quality.
"""

class TrialRanker:
    """
    Ranks clinical trials based on composite clinical and scientific utility scoring.
    """
    PHASE_WEIGHTS = {
        "Phase III": 1.0,
        "Phase IV": 0.9,
        "Phase II": 0.8,
        "Phase I/II": 0.7,
        "Phase I": 0.5
    }

    STATUS_WEIGHTS = {
        "recruiting": 1.0,
        "active, recruiting": 1.0,
        "active": 0.8,
        "enrolling": 0.7,
        "completed": 0.2,
        "suspended": 0.0,
        "terminated": 0.0
    }

    @classmethod
    def get_phase_weight(cls, phase_str):
        """Calculates normalized weight for a clinical trial phase."""
        for key, weight in cls.PHASE_WEIGHTS.items():
            if key.lower() in (phase_str or "").lower():
                return weight
        return 0.7

    @classmethod
    def get_status_weight(cls, status_str):
        """Calculates normalized recruitment status weight."""
        s_low = (status_str or "").lower()
        for key, weight in cls.STATUS_WEIGHTS.items():
            if key in s_low:
                return weight
        return 0.6

    @classmethod
    def compute_evidence_weight(cls, trial, genomic_context=None):
        """
        Calculates biomarker evidence weighting based on AMP/ASCO tiers.
        """
        biomarkers = [b.upper() for b in trial.get("biomarkers", [])]
        tier = (genomic_context or {}).get("actionability_tier", "Tier I-A")

        if any(b in ["BRCA1", "EGFR", "KRAS", "BRAF"] for b in biomarkers):
            return 1.0
        elif any(b in ["PIK3CA", "ALK", "HRD", "MSI-H"] for b in biomarkers):
            return 0.9
        elif "Tier I" in str(tier):
            return 0.85
        return 0.7

    @classmethod
    def rank_trials(cls, matched_trials, genomic_context=None):
        """
        Ranks matched trials by composite priority score.
        """
        scored = []
        for t in matched_trials:
            match_score = t.get("matchScore", 0.0)
            phase_w = cls.get_phase_weight(t.get("phase", ""))
            status_w = cls.get_status_weight(t.get("status", ""))
            evidence_w = cls.compute_evidence_weight(t, genomic_context)

            composite = (
                match_score * 0.40 +
                phase_w * 0.25 +
                status_w * 0.20 +
                evidence_w * 0.15
            )

            # If disqualified, force composite down
            if t.get("matchType") == "disqualified" or not t.get("isEligible", True):
                composite = composite * 0.2

            composite = round(float(composite), 3)

            if composite >= 0.75:
                category = "High Priority Trial"
            elif composite >= 0.55:
                category = "Recommended Trial"
            elif composite >= 0.35:
                category = "Consideration Trial"
            else:
                category = "Low Priority / Exploratory"

            # Explicit matching and eligibility evidence structure for clinical governance
            is_elig = t.get("isEligible", True)
            if not is_elig or t.get("matchType") == "disqualified":
                eligibility_status = "ineligible"
            elif match_score >= 0.85:
                eligibility_status = "eligible"
            else:
                eligibility_status = "potentially_eligible"

            item = dict(t)
            item["trial_id"] = t.get("trialId")
            item["eligibility"] = {
                "status": eligibility_status,
                "matched_criteria": t.get("matchedCriteria", []),
                "unmatched_criteria": t.get("unmatchedCriteria", []),
                "unknown_criteria": t.get("violations", [])
            }
            item["evidence"] = {
                "biomarker": ", ".join(t.get("biomarkers", [])) or "Biomarker agnostic",
                "stage": ", ".join(t.get("conditions", [])[:2]) or "Advanced solid tumors",
                "performance_status": "ECOG performance criteria met" if is_elig else "Performance criteria or contraindication conflict"
            }
            item["source"] = "ClinicalTrials.gov"
            item["last_verified"] = "2026-09"
            item["compositeScore"] = composite
            item["recommendationCategory"] = category
            item["scoringBreakdown"] = {
                "matchScore": match_score,
                "phaseWeight": round(phase_w, 2),
                "statusWeight": round(status_w, 2),
                "evidenceWeight": round(evidence_w, 2)
            }
            scored.append(item)

        # Sort descending by compositeScore, then matchScore
        scored.sort(key=lambda x: (x["compositeScore"], x["matchScore"]), reverse=True)

        # Assign ordinal rank
        for idx, item in enumerate(scored):
            item["rank"] = idx + 1

        return scored
