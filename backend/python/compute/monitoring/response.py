"""
Response Evaluation module for PERSEPHONE Clinical Monitoring & Longitudinal Intelligence.
Evaluates RECIST 1.1 response status, best overall response (BOR), depth of response,
and duration of response across longitudinal imaging checkpoints.
"""

class TreatmentResponseEvaluator:
    """
    Applies RECIST 1.1 criteria to classify longitudinal tumor response categories.
    """

    @classmethod
    def evaluate_response(cls, trajectory_analysis):
        """
        Consumes tumor trajectory analysis and determines RECIST 1.1 category and metrics.
        """
        trajectory = trajectory_analysis.get("trajectory", [])
        if not trajectory:
            return {
                "currentStatus": "NE",
                "bestOverallResponse": "NE",
                "depthOfResponsePercent": 0.0,
                "durationOfResponseDays": 0,
                "evaluations": []
            }

        baseline_vol = trajectory_analysis.get("baselineVolume", trajectory[0]["volume"])
        nadir_vol = trajectory_analysis.get("nadirVolume", baseline_vol)
        nadir_day = trajectory_analysis.get("nadirDay", 0)

        evaluations = []
        best_response = "SD"
        first_response_day = None
        progression_day = None

        for pt in trajectory:
            vol = pt["volume"]
            pct_base = round(((vol - baseline_vol) / max(baseline_vol, 0.001)) * 100.0, 1)
            pct_nadir = round(((vol - nadir_vol) / max(nadir_vol, 0.001)) * 100.0, 1)

            # RECIST 1.1 classification: post-nadir increase takes precedence for progression
            if pt["day"] > nadir_day and pct_nadir >= 20.0 and (vol - nadir_vol) >= 5.0:
                recist = "PD"
            elif pct_base <= -90.0 or vol <= 10.0:
                recist = "CR"
            elif pct_base <= -30.0:
                recist = "PR"
            else:
                recist = "SD"

            # Track Best Overall Response
            if recist == "CR":
                best_response = "CR"
                if first_response_day is None:
                    first_response_day = pt["day"]
            elif recist == "PR" and best_response != "CR":
                best_response = "PR"
                if first_response_day is None:
                    first_response_day = pt["day"]
            elif recist == "PD" and progression_day is None:
                progression_day = pt["day"]

            evaluations.append({
                "day": pt["day"],
                "date": pt.get("date"),
                "volume": vol,
                "percentChangeFromBaseline": pct_base,
                "percentChangeFromNadir": pct_nadir,
                "recistStatus": recist
            })

        current_status = evaluations[-1]["recistStatus"]

        # Duration of response
        dor_days = 0
        if first_response_day is not None:
            end_day = progression_day if progression_day is not None else evaluations[-1]["day"]
            dor_days = max(0, end_day - first_response_day)

        depth_of_response = round(((baseline_vol - nadir_vol) / max(baseline_vol, 0.001)) * 100.0, 1)

        return {
            "currentStatus": current_status,
            "bestOverallResponse": best_response,
            "depthOfResponsePercent": depth_of_response,
            "durationOfResponseDays": dor_days,
            "isResponding": current_status in ["CR", "PR"],
            "hasProgressed": current_status == "PD",
            "evaluations": evaluations
        }
