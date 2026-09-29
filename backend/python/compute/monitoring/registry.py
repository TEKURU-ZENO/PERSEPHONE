"""
Monitoring Registry module for PERSEPHONE Clinical Monitoring & Longitudinal Intelligence.
Provides unified dispatch and telemetry profiling for monitoring pipeline endpoints.
"""
import time
from backend.python.compute.monitoring.monitor import ClinicalMonitor
from backend.python.compute.monitoring.timeline import PatientTimeline
from backend.python.compute.monitoring.trajectory import TumorTrajectoryAnalyzer
from backend.python.compute.monitoring.response import TreatmentResponseEvaluator
from backend.python.compute.monitoring.alerts import ClinicalAlertGenerator

class MonitoringRegistry:
    """
    Public registry interface for Clinical Monitoring compute routines.
    """

    @classmethod
    def get_timeline(cls, patient_id="patient-a"):
        """Returns the complete longitudinal timeline for a patient."""
        start = time.perf_counter()
        timeline = PatientTimeline.get_patient_timeline(patient_id)
        elapsed = round((time.perf_counter() - start) * 1000, 2)
        return {
            "patientId": str(patient_id),
            "timeline": timeline,
            "totalEvents": len(timeline),
            "processingTimeMs": elapsed
        }

    @classmethod
    def get_response(cls, patient_id="patient-a"):
        """Evaluates RECIST 1.1 treatment response status from timeline trajectory."""
        start = time.perf_counter()
        timeline = PatientTimeline.get_patient_timeline(patient_id)
        trajectory = TumorTrajectoryAnalyzer.analyze_trajectory(timeline)
        response = TreatmentResponseEvaluator.evaluate_response(trajectory)
        elapsed = round((time.perf_counter() - start) * 1000, 2)
        return {
            "patientId": str(patient_id),
            "trajectory": trajectory,
            "response": response,
            "processingTimeMs": elapsed
        }

    @classmethod
    def get_alerts(cls, patient_id="patient-a"):
        """Generates prioritized clinical alerts for the patient."""
        start = time.perf_counter()
        state = ClinicalMonitor.evaluate_patient_state(patient_id)
        elapsed = round((time.perf_counter() - start) * 1000, 2)
        return {
            "patientId": str(patient_id),
            "alerts": state["alerts"],
            "summaryMetrics": state["summaryMetrics"],
            "processingTimeMs": elapsed
        }

    @classmethod
    def run_comprehensive_monitoring(cls, patient_data=None):
        """Runs the full longitudinal monitoring engine."""
        start = time.perf_counter()
        pid = (patient_data or {}).get("id", "patient-a")
        state = ClinicalMonitor.evaluate_patient_state(pid)
        elapsed = round((time.perf_counter() - start) * 1000, 2)
        state["processingTimeMs"] = elapsed
        return state
