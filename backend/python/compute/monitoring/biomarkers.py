"""
Biomarkers module for PERSEPHONE Clinical Monitoring & Longitudinal Intelligence.
Analyzes serum tumor marker kinetics (CA-125) and liquid biopsy ctDNA VAF dynamics.
"""

class BiomarkerKineticsAnalyzer:
    """
    Evaluates longitudinal biomarker trajectories, clearance rates, and clonal kinetics.
    """

    @classmethod
    def analyze_biomarkers(cls, timeline):
        """
        Extracts CA-125 and ctDNA VAF series and computes clearance and inflection metrics.
        """
        ca125_points = []
        vaf_points = []

        for e in timeline:
            m = e.get("metrics", {})
            day = e.get("day", 0)
            date = e.get("date")

            if "ca125" in m:
                ca125_points.append({"day": day, "date": date, "value": float(m["ca125"])})
            if "ctdnaVaf" in m:
                vaf_points.append({"day": day, "date": date, "value": float(m["ctdnaVaf"])})

        # Process CA-125
        ca125_analysis = cls._analyze_series(ca125_points, normal_threshold=35.0)

        # Process ctDNA VAF
        vaf_analysis = cls._analyze_series(vaf_points, normal_threshold=0.1)

        # Molecular recurrence check
        molecular_relapse = False
        if vaf_analysis["points"]:
            min_vaf = vaf_analysis["nadir"]
            curr_vaf = vaf_analysis["current"]
            if curr_vaf > 1.0 and curr_vaf >= (min_vaf * 3.0):
                molecular_relapse = True

        return {
            "ca125": ca125_analysis,
            "ctdnaVaf": vaf_analysis,
            "molecularRelapseDetected": molecular_relapse,
            "hasElevatedBiomarkers": ca125_analysis["isElevated"] or vaf_analysis["isElevated"]
        }

    @classmethod
    def _analyze_series(cls, points, normal_threshold):
        if not points:
            return {"points": [], "baseline": 0, "nadir": 0, "current": 0, "isElevated": False, "velocity": 0.0}

        points.sort(key=lambda x: x["day"])
        baseline = points[0]["value"]
        current = points[-1]["value"]
        nadir = min(p["value"] for p in points)

        velocity = 0.0
        if len(points) >= 2:
            dt = max(points[-1]["day"] - points[-2]["day"], 1)
            velocity = round((current - points[-2]["value"]) / dt, 3)

        return {
            "points": points,
            "baseline": baseline,
            "nadir": nadir,
            "current": current,
            "velocity": velocity,
            "isElevated": current > normal_threshold,
            "percentReductionFromBaseline": round(((baseline - nadir) / max(baseline, 0.001)) * 100.0, 1),
            "reboundFromNadir": round(((current - nadir) / max(nadir, 0.001)) * 100.0, 1) if nadir < current else 0.0
        }
