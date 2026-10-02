"""
Temporal Evidence Validity module for PERSEPHONE Research Intelligence Platform.
Tracks validity windows (effective_from, effective_until, superseded_by) across guidelines and evidence.
"""
import time
from typing import Dict, Any, Optional


class TemporalValidityEngine:
    """
    Evaluates temporal validity windows to ensure outdated or superseded clinical guidelines
    and clinical trials are appropriately flagged or downgraded.
    """

    @classmethod
    def evaluate_temporal_validity(
        cls,
        effective_from: str,
        effective_until: Optional[str] = None,
        superseded_by: Optional[str] = None,
        reference_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Determines if an evidence item or guideline is CURRENT, SUPERSEDED, or EXPIRED.
        """
        now_str = reference_date or time.strftime("%Y-%m-%d", time.gmtime())

        is_superseded = bool(superseded_by)
        is_expired = bool(effective_until and effective_until < now_str)
        is_future = bool(effective_from and effective_from > now_str)

        if is_superseded:
            status = "SUPERSEDED"
            rationale = f"Superseded by newer guideline version: {superseded_by}."
        elif is_expired:
            status = "EXPIRED"
            rationale = f"Validity window lapsed on {effective_until}."
        elif is_future:
            status = "PRE_RELEASE"
            rationale = f"Becomes effective on {effective_from}."
        else:
            status = "CURRENT"
            rationale = f"Active clinical guidance in effect since {effective_from}."

        return {
            "validity_status": status,
            "is_actionable": status == "CURRENT",
            "effective_from": effective_from,
            "effective_until": effective_until,
            "superseded_by": superseded_by,
            "evaluated_at": now_str,
            "rationale": rationale
        }
