import unittest
from backend.python.compute.monitoring.timeline import PatientTimeline
from backend.python.compute.monitoring.treatment_cycles import TreatmentCycleTracker
from backend.python.compute.monitoring.trajectory import TumorTrajectoryAnalyzer
from backend.python.compute.monitoring.response import TreatmentResponseEvaluator
from backend.python.compute.monitoring.toxicity import ToxicityTracker
from backend.python.compute.monitoring.biomarkers import BiomarkerKineticsAnalyzer
from backend.python.compute.monitoring.progression import ProgressionDetector
from backend.python.compute.monitoring.alerts import ClinicalAlertGenerator
from backend.python.compute.monitoring.monitor import ClinicalMonitor
from backend.python.compute.monitoring.registry import MonitoringRegistry

class TestPatientTimeline(unittest.TestCase):
    def test_get_elena_timeline(self):
        timeline = PatientTimeline.get_patient_timeline("patient-a")
        self.assertIsInstance(timeline, list)
        self.assertGreaterEqual(len(timeline), 10)
        categories = set(e.get("category") for e in timeline)
        self.assertIn("diagnosis", categories)
        self.assertIn("treatment", categories)
        self.assertIn("imaging", categories)
        self.assertIn("toxicity", categories)
        self.assertIn("genomics", categories)

    def test_get_metrics_stream(self):
        timeline = PatientTimeline.get_patient_timeline("patient-a")
        vol_stream = PatientTimeline.get_metrics_stream(timeline, "tumorVolume")
        self.assertGreaterEqual(len(vol_stream), 4)
        self.assertEqual(vol_stream[0]["day"], 0)
        self.assertEqual(vol_stream[0]["value"], 82.0)

class TestTreatmentCycleTracker(unittest.TestCase):
    def test_analyze_cycles(self):
        timeline = PatientTimeline.get_patient_timeline("patient-a")
        res = TreatmentCycleTracker.analyze_cycles(timeline)
        self.assertIn("cycles", res)
        self.assertGreater(res["totalCyclesDelivered"], 0)
        self.assertGreater(res["averageRdi"], 0.8)
        self.assertIn("totalDelayDays", res)

class TestTumorTrajectory(unittest.TestCase):
    def test_analyze_trajectory(self):
        timeline = PatientTimeline.get_patient_timeline("patient-a")
        res = TumorTrajectoryAnalyzer.analyze_trajectory(timeline)
        self.assertIn("trajectory", res)
        self.assertEqual(res["baselineVolume"], 82.0)
        self.assertEqual(res["nadirVolume"], 8.0)
        self.assertEqual(res["nadirDay"], 180)
        self.assertEqual(res["trend"], "Progressing")
        self.assertGreater(res["currentVelocity"], 0.0)

class TestTreatmentResponse(unittest.TestCase):
    def test_evaluate_response(self):
        timeline = PatientTimeline.get_patient_timeline("patient-a")
        traj = TumorTrajectoryAnalyzer.analyze_trajectory(timeline)
        res = TreatmentResponseEvaluator.evaluate_response(traj)
        self.assertIn("bestOverallResponse", res)
        self.assertIn(res["bestOverallResponse"], ["PR", "CR"])
        self.assertEqual(res["currentStatus"], "PD")
        self.assertTrue(res["hasProgressed"])
        self.assertGreater(res["depthOfResponsePercent"], 80.0)

class TestToxicityTracker(unittest.TestCase):
    def test_evaluate_toxicities(self):
        timeline = PatientTimeline.get_patient_timeline("patient-a")
        res = ToxicityTracker.evaluate_toxicities(timeline)
        self.assertIn("records", res)
        self.assertEqual(res["maxGradeObserved"], 2)
        self.assertFalse(res["hasSevereToxicity"])
        self.assertGreater(res["cumulativeToxicityScore"], 0.0)

class TestBiomarkers(unittest.TestCase):
    def test_analyze_biomarkers(self):
        timeline = PatientTimeline.get_patient_timeline("patient-a")
        res = BiomarkerKineticsAnalyzer.analyze_biomarkers(timeline)
        self.assertIn("ca125", res)
        self.assertIn("ctdnaVaf", res)
        self.assertTrue(res["molecularRelapseDetected"])
        self.assertTrue(res["hasElevatedBiomarkers"])

class TestProgression(unittest.TestCase):
    def test_evaluate_progression(self):
        timeline = PatientTimeline.get_patient_timeline("patient-a")
        traj = TumorTrajectoryAnalyzer.analyze_trajectory(timeline)
        resp = TreatmentResponseEvaluator.evaluate_response(traj)
        bio = BiomarkerKineticsAnalyzer.analyze_biomarkers(timeline)
        prog = ProgressionDetector.evaluate_progression(traj, resp, bio)
        self.assertEqual(prog["signalLevel"], "CONFIRMED_PROGRESSION")
        self.assertTrue(prog["hasRadiologicProgression"])
        self.assertEqual(prog["leadTimeDays"], 60)

class TestAlerts(unittest.TestCase):
    def test_generate_alerts(self):
        timeline = PatientTimeline.get_patient_timeline("patient-a")
        traj = TumorTrajectoryAnalyzer.analyze_trajectory(timeline)
        resp = TreatmentResponseEvaluator.evaluate_response(traj)
        tox = ToxicityTracker.evaluate_toxicities(timeline)
        bio = BiomarkerKineticsAnalyzer.analyze_biomarkers(timeline)
        prog = ProgressionDetector.evaluate_progression(traj, resp, bio)
        alerts = ClinicalAlertGenerator.generate_alerts(traj, resp, tox, bio, prog)
        self.assertGreater(len(alerts), 0)
        # Verify CRITICAL is first
        self.assertEqual(alerts[0]["severity"], "CRITICAL")

class TestClinicalMonitorAndRegistry(unittest.TestCase):
    def test_end_to_end_monitoring(self):
        state = ClinicalMonitor.evaluate_patient_state("patient-a")
        self.assertIn("timeline", state)
        self.assertIn("trajectory", state)
        self.assertIn("response", state)
        self.assertIn("toxicity", state)
        self.assertIn("biomarkers", state)
        self.assertIn("progression", state)
        self.assertIn("alerts", state)
        self.assertIn("summaryMetrics", state)

    def test_monitoring_registry_methods(self):
        tl = MonitoringRegistry.get_timeline("patient-a")
        self.assertIn("timeline", tl)
        resp = MonitoringRegistry.get_response("patient-a")
        self.assertIn("response", resp)
        al = MonitoringRegistry.get_alerts("patient-a")
        self.assertIn("alerts", al)

if __name__ == '__main__':
    unittest.main()
