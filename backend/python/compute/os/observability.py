"""
OS Observability and System Telemetry Module for PERSEPHONE OS.
Provides live health monitoring, plane latencies, error tracking, and degraded mode detection.
"""
from typing import Dict, List, Any
import time
import threading
from backend.python.compute.os.planes import PlaneType


class OSObservabilityMonitor:
    """
    Subsystem observability and telemetry collector for PERSEPHONE OS.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(OSObservabilityMonitor, cls).__new__(cls)
                cls._instance._plane_latencies = {p.value: [] for p in PlaneType}
                cls._instance._error_counts = {p.value: 0 for p in PlaneType}
                cls._instance._total_runs = 0
                cls._instance._abstained_runs = 0
                cls._instance._supported_runs = 0
                cls._instance._start_time = time.time()
            return cls._instance

    def record_run(self, execution_time_ms: float, status: str, plane_metrics: Dict[str, float] = None):
        """Records an execution episode and updates rolling metrics."""
        with self._lock:
            self._total_runs += 1
            if status == "ABSTAIN":
                self._abstained_runs += 1
            elif status in ["SUPPORTED", "APPROVED"]:
                self._supported_runs += 1

            if plane_metrics:
                for plane, lat in plane_metrics.items():
                    if plane in self._plane_latencies:
                        self._plane_latencies[plane].append(lat)
                        if len(self._plane_latencies[plane]) > 100:
                            self._plane_latencies[plane].pop(0)

    def record_error(self, plane: str, error_msg: str):
        """Records an error event in a plane."""
        with self._lock:
            if plane in self._error_counts:
                self._error_counts[plane] += 1

    def get_system_health(self) -> Dict[str, Any]:
        """Provides an authoritative snapshot of system health for the OS Cockpit."""
        with self._lock:
            uptime_seconds = int(time.time() - self._start_time)
            plane_status = {}

            overall_status = "NOMINAL"
            total_errors = sum(self._error_counts.values())

            for plane in PlaneType:
                latencies = self._plane_latencies[plane.value]
                avg_lat = round(sum(latencies) / len(latencies), 2) if latencies else 0.0
                errs = self._error_counts[plane.value]

                p_status = "HEALTHY" if errs == 0 else ("DEGRADED" if errs < 3 else "UNHEALTHY")
                if p_status != "HEALTHY":
                    overall_status = "DEGRADED"

                plane_status[plane.value] = {
                    "status": p_status,
                    "avg_latency_ms": avg_lat,
                    "error_count": errs,
                    "sample_count": len(latencies)
                }

            abstention_rate = round(self._abstained_runs / max(1, self._total_runs), 3)

            return {
                "os_name": "PERSEPHONE OS",
                "os_version": "v1.0",
                "overall_status": overall_status,
                "uptime_seconds": uptime_seconds,
                "total_runs_monitored": self._total_runs,
                "supported_runs": self._supported_runs,
                "abstained_runs": self._abstained_runs,
                "abstention_rate": abstention_rate,
                "total_system_errors": total_errors,
                "planes": plane_status,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
