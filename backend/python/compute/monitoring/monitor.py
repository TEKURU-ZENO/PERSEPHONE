"""
Clinical Monitor module for PERSEPHONE Clinical Monitoring & Longitudinal Intelligence.
Coordinates multi-stream longitudinal data processing and generates a unified LongitudinalPatientState.
"""
from backend.python.compute.monitoring.timeline import PatientTimeline
from backend.python.compute.monitoring.treatment_cycles import TreatmentCycleTracker
from backend.python.compute.monitoring.trajectory import TumorTrajectoryAnalyzer
from backend.python.compute.monitoring.response import TreatmentResponseEvaluator
from backend.python.compute.monitoring.toxicity import ToxicityTracker
from backend.python.compute.monitoring.biomarkers import BiomarkerKineticsAnalyzer
from backend.python.compute.monitoring.progression import ProgressionDetector
from backend.python.compute.monitoring.alerts import ClinicalAlertGenerator

class ClinicalMonitor:
    """
    Main composite monitoring engine integrating all longitudinal analytical streams.
    """

    @classmethod
    def evaluate_patient_state(cls, patient_id="patient-a"):
        """
        Executes end-to-end longitudinal state evaluation for a patient.
        """
        timeline = PatientTimeline.get_patient_timeline(patient_id)

        # 1. Treatment cycles & adherence
        cycles = TreatmentCycleTracker.analyze_cycles(timeline)

        # 2. Tumor volume kinetics & velocity
        trajectory = TumorTrajectoryAnalyzer.analyze_trajectory(timeline)

        # 3. RECIST 1.1 response status
        response = TreatmentResponseEvaluator.evaluate_response(trajectory)

        # 4. CTCAE adverse events & cumulative toxicity
        toxicity = ToxicityTracker.evaluate_toxicities(timeline)

        # 5. Serum markers & ctDNA VAF kinetics
        biomarkers = BiomarkerKineticsAnalyzer.analyze_biomarkers(timeline)

        # 6. Early progression detection & lead-times
        progression = ProgressionDetector.evaluate_progression(trajectory, response, biomarkers)

        # 7. Clinical alerts stream
        alerts = ClinicalAlertGenerator.generate_alerts(trajectory, response, toxicity, biomarkers, progression)

        summary_metrics = {
            "currentVolume": trajectory.get("currentVolume"),
            "currentVelocity": trajectory.get("currentVelocity"),
            "bestResponse": response.get("bestOverallResponse"),
            "currentResponse": response.get("currentStatus"),
            "maxToxicityGrade": toxicity.get("maxGradeObserved"),
            "currentCa125": biomarkers.get("ca125", {}).get("current"),
            "currentVaf": biomarkers.get("ctdnaVaf", {}).get("current"),
            "progressionSignal": progression.get("signalLevel"),
            "totalAlerts": len(alerts),
            "criticalAlertsCount": sum(1 for a in alerts if a["severity"] == "CRITICAL")
        }

        return {
            "patientId": str(patient_id),
            "timeline": timeline,
            "cycles": cycles,
            "trajectory": trajectory,
            "response": response,
            "toxicity": toxicity,
            "biomarkers": biomarkers,
            "progression": progression,
            "alerts": alerts,
            "summaryMetrics": summary_metrics
        }
