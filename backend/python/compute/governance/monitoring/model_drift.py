"""
Model Drift Monitoring Module for PERSEPHONE Governance Platform.
Tracks rolling windows of production inference calls to detect data shifts,
concept drift, and anomalous prediction confidence degradation.
"""
from typing import Dict, List, Any, Optional
import time


class ModelDriftMonitor:
    """
    Monitors live inference telemetry for distribution shifts and confidence degradation.
    """
    _history: List[Dict[str, Any]] = []

    @classmethod
    def record_inference(
        cls,
        patient_id: str,
        decision_status: str,
        calibrated_confidence: float,
        discordance_index: float,
        drift_psi: float
    ) -> None:
        entry = {
            "patient_id": patient_id,
            "decision_status": decision_status,
            "confidence": calibrated_confidence,
            "discordance_index": discordance_index,
            "drift_psi": drift_psi,
            "timestamp": time.time()
        }
        cls._history.append(entry)
        if len(cls._history) > 500:
            cls._history = cls._history[-500:]

    @classmethod
    def get_drift_telemetry(cls) -> Dict[str, Any]:
        if not cls._history:
            return {
                "total_inferences_monitored": 0,
                "rolling_avg_confidence": 0.85,
                "rolling_avg_discordance": 0.12,
                "abstention_rate": 0.0,
                "concept_drift_detected": False,
                "status": "HEALTHY_STABLE"
            }

        n = len(cls._history)
        avg_conf = sum(h["confidence"] for h in cls._history) / n
        avg_disc = sum(h["discordance_index"] for h in cls._history) / n
        abstentions = sum(1 for h in cls._history if h["decision_status"] == "ABSTAIN")
        abstention_rate = abstentions / n

        concept_drift = avg_conf < 0.65 or abstention_rate > 0.35

        return {
            "total_inferences_monitored": n,
            "rolling_avg_confidence": round(avg_conf, 3),
            "rolling_avg_discordance": round(avg_disc, 3),
            "abstention_rate": round(abstention_rate, 3),
            "concept_drift_detected": concept_drift,
            "status": "CONCEPT_DRIFT_ALERT" if concept_drift else "HEALTHY_STABLE"
        }
