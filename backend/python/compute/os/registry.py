"""
OS Registry Module for PERSEPHONE OS.
Top-level static entrypoint wrapping Kernel, Observability, Planes, Manifest, and Replay engines.
"""
from typing import Dict, Any, Optional
import time
from backend.python.compute.common.metrics import profile_compute
from backend.python.compute.os.kernel import PersephoneKernel
from backend.python.compute.os.planes import PlaneRegistry
from backend.python.compute.os.observability import OSObservabilityMonitor
from backend.python.compute.os.manifest import ExperimentManifestEngine
from backend.python.compute.os.replay import CaseReplayEngine
from backend.python.compute.os.event_bus import OSEventBus
from backend.python.compute.os.context import ClinicalCaseContext
from backend.python.compute.os.contracts.case import CaseSchemaValidator


class OSRegistry:
    """
    Central static entrypoint for all OS-level scientific compute invocations.
    """
    _kernel = PersephoneKernel()
    _observability = OSObservabilityMonitor()
    _event_bus = OSEventBus()

    @classmethod
    def run_pipeline(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Runs a complete clinical case through the PersephoneKernel DAG."""
        start = time.perf_counter()
        result = cls._kernel.run_case_pipeline(data)
        metrics = profile_compute(start, algorithm="OS_Kernel_Pipeline")
        return {
            "status": result.get("status", "COMPLETED"),
            "governance": result.get("governance", {}),
            "manifest_id": result.get("manifest_id"),
            "result": result,
            "metadata": metrics
        }

    @classmethod
    def get_health(cls, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Returns the authoritative system observability and plane health snapshot."""
        start = time.perf_counter()
        health = cls._observability.get_system_health()
        metrics = profile_compute(start, algorithm="OS_Health_Check")
        return {
            "status": "HEALTHY" if health.get("overall_status") == "NOMINAL" else health.get("overall_status", "HEALTHY"),
            "council_agents": 23,
            "planes": 5,
            "result": health,
            "metadata": metrics
        }

    @classmethod
    def get_planes(cls, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Returns the 5 Planes topology and AgentSpec dependency graph."""
        start = time.perf_counter()
        topology = PlaneRegistry.get_plane_telemetry_topology()
        metrics = profile_compute(start, algorithm="OS_Planes_Topology")
        return {
            "planes": topology,
            "result": topology,
            "metadata": metrics
        }

    @classmethod
    def get_events(cls, data: Optional[Dict[str, Any]] = None, limit: int = 100) -> Dict[str, Any]:
        """Returns recent events from the OSEventBus stream."""
        start = time.perf_counter()
        if isinstance(data, dict):
            run_id = data.get("run_id")
            lim = int(data.get("limit", limit))
        else:
            run_id = None
            lim = limit
        events = cls._event_bus.get_events(run_id=run_id, limit=lim)
        metrics = profile_compute(start, algorithm="OS_Events_Stream")
        return {
            "events": events,
            "result": events,
            "metadata": metrics
        }

    @classmethod
    def generate_manifest(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generates an ExperimentManifest and computes its SHA-256 seal."""
        start = time.perf_counter()
        patient = data.get("patient") or data.get("case") or data
        context = ClinicalCaseContext(
            case_id=str(patient.get("id", "patient-normal")),
            patient_twin=patient,
            inputs=data
        )
        manifest = ExperimentManifestEngine.generate_manifest(context)
        metrics = profile_compute(start, algorithm="OS_Manifest_Generation")
        return {
            "result": manifest,
            "manifest": manifest,
            "metadata": metrics
        }

    @classmethod
    def replay_case(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Executes deterministic case replay and validates mathematical parity."""
        start = time.perf_counter()
        manifest = data.get("manifest")
        if not manifest:
            # Generate a baseline manifest if not explicitly provided
            patient = data.get("patient") or data.get("case") or data
            context = ClinicalCaseContext(
                case_id=str(patient.get("id", "patient-normal")),
                patient_twin=patient,
                inputs=data
            )
            manifest = ExperimentManifestEngine.generate_manifest(context)

        replay_result = CaseReplayEngine.replay_case(manifest, raw_inputs=data)
        metrics = profile_compute(start, algorithm="OS_Case_Replay")
        return {
            "result": replay_result,
            "replay": replay_result,
            "metadata": metrics
        }
