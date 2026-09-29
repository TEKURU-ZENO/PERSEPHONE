"""
Treatment Cycles module for PERSEPHONE Clinical Monitoring & Longitudinal Intelligence.
Analyzes systemic therapy cycles, relative dose intensity (RDI), cycle delays,
dose adjustments, and treatment interruptions.
"""

class TreatmentCycleTracker:
    """
    Evaluates cycle-by-cycle chemotherapy and targeted therapy administration.
    """

    @classmethod
    def analyze_cycles(cls, timeline):
        """
        Extracts treatment events and computes relative dose intensity and delay patterns.
        """
        treatment_events = [e for e in timeline if e.get("category") == "treatment"]
        toxicity_events = [e for e in timeline if e.get("category") == "toxicity"]

        cycles = []
        cycle_idx = 1
        total_delay_days = 0
        cumulative_rdi = 0.0

        expected_interval_days = 21  # Standard 3-weekly cycle assumption

        for i, ev in enumerate(treatment_events):
            metrics = ev.get("metrics", {})
            dose_intensity = metrics.get("doseIntensity", 1.0)
            day = ev.get("day", 0)

            # Calculate delay relative to standard 21-day schedule
            delay = 0
            if i > 0:
                actual_interval = day - treatment_events[i - 1].get("day", 0)
                if actual_interval > expected_interval_days:
                    delay = actual_interval - expected_interval_days
                    total_delay_days += delay

            # Check if there was an associated toxicity triggering this delay
            reason = "Scheduled"
            if delay > 0:
                matching_tox = [t for t in toxicity_events if abs(t["day"] - day) <= 14]
                if matching_tox:
                    reason = f"Delayed by {delay}d: {matching_tox[0]['title']}"
                else:
                    reason = f"Delayed by {delay}d (Clinical hold)"

            is_interruption = delay >= 14

            cycles.append({
                "cycleNumber": cycle_idx,
                "title": ev.get("title"),
                "day": day,
                "date": ev.get("date"),
                "relativeDoseIntensity": round(dose_intensity, 2),
                "delayDays": delay,
                "delayReason": reason,
                "isInterruption": is_interruption,
                "status": "Completed"
            })
            cumulative_rdi += dose_intensity
            cycle_idx += 1

        avg_rdi = round(cumulative_rdi / max(len(cycles), 1), 3)

        return {
            "cycles": cycles,
            "totalCyclesDelivered": len(cycles),
            "averageRdi": avg_rdi,
            "totalDelayDays": total_delay_days,
            "hasTreatmentInterruptions": any(c["isInterruption"] for c in cycles),
            "adherenceScore": round(max(0.0, 1.0 - (total_delay_days * 0.02) - ((1.0 - avg_rdi) * 0.5)), 2)
        }
