"""
Toxicity module for PERSEPHONE Clinical Monitoring & Longitudinal Intelligence.
Tracks CTCAE v5.0 adverse events, cumulative organ toxicity burdens,
and dose-limiting toxicity (DLT) occurrences.
"""

class ToxicityTracker:
    """
    Evaluates longitudinal adverse events and cumulative patient toxicity burden.
    """

    @classmethod
    def evaluate_toxicities(cls, timeline):
        """
        Parses timeline for toxicity events and computes cumulative and organ-specific burden.
        """
        tox_events = [e for e in timeline if e.get("category") == "toxicity"]

        records = []
        max_grade = 0
        organ_burdens = {}
        dlts = []

        for e in tox_events:
            metrics = e.get("metrics", {})
            grade = metrics.get("ctcaeGrade", 1)
            tox_type = metrics.get("toxicityType", "constitutional")
            day = e.get("day", 0)

            max_grade = max(max_grade, grade)
            organ_burdens[tox_type] = organ_burdens.get(tox_type, 0) + grade

            is_dlt = grade >= 3 or metrics.get("doseLimiting", False)
            if is_dlt:
                dlts.append({"day": day, "title": e.get("title"), "grade": grade})

            records.append({
                "day": day,
                "date": e.get("date"),
                "title": e.get("title"),
                "details": e.get("details"),
                "grade": grade,
                "organSystem": tox_type,
                "isDlt": is_dlt
            })

        # Calculate cumulative burden score (normalized index 0 to 10)
        cumulative_score = min(10.0, round(sum(r["grade"] * 1.5 for r in records), 1))

        current_grade = records[-1]["grade"] if records else 0

        return {
            "records": records,
            "totalAdverseEvents": len(records),
            "maxGradeObserved": max_grade,
            "currentGrade": current_grade,
            "cumulativeToxicityScore": cumulative_score,
            "hasSevereToxicity": max_grade >= 3,
            "doseLimitingToxicities": dlts,
            "organSystemBurdens": organ_burdens
        }
