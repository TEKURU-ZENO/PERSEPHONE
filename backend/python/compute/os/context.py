"""
Clinical Case Context Module for PERSEPHONE OS.
Defines the authoritative unit of execution across all planes and agents.
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import time
from backend.python.compute.ai_runtime.agents.blackboard import BlackboardMemory
from backend.python.compute.os.contracts.case import ExecutionRunMetadata


class PipelineState(str, Enum):
    INITIALIZING = "initializing"
    INGESTING = "ingesting"
    ANALYZING = "analyzing"
    SIMULATING = "simulating"
    EVALUATING = "evaluating"
    GOVERNANCE_CHECK = "governance_check"
    CLINICIAN_REVIEW = "clinician_review"
    REPORTING = "reporting"
    COMPLETED = "completed"
    ABSTAINED = "abstained"
    FAILED = "failed"


@dataclass
class ClinicalCaseContext:
    """
    Authoritative state container representing a clinical case execution run.
    Eliminates redundant state reconstruction by agents.
    """
    case_id: str
    run_id: str = field(default_factory=lambda: f"RUN-{int(time.time()*1000)}")
    patient_twin: Dict[str, Any] = field(default_factory=dict)
    inputs: Dict[str, Any] = field(default_factory=dict)
    blackboard: BlackboardMemory = field(default_factory=BlackboardMemory)
    evidence_graph: Dict[str, Any] = field(default_factory=dict)
    simulation_state: Dict[str, Any] = field(default_factory=dict)
    agent_states: Dict[str, Any] = field(default_factory=dict)
    governance_state: Dict[str, Any] = field(default_factory=dict)
    provenance_trail: List[Dict[str, Any]] = field(default_factory=list)
    telemetry: Dict[str, Any] = field(default_factory=dict)
    execution_status: PipelineState = PipelineState.INITIALIZING
    idempotency_key: Optional[str] = None
    created_at: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))

    @property
    def pipeline_state(self) -> PipelineState:
        return self.execution_status

    @pipeline_state.setter
    def pipeline_state(self, val: PipelineState):
        self.execution_status = val

    @classmethod
    def create(cls, raw_payload: Dict[str, Any], run_meta: Optional[ExecutionRunMetadata] = None) -> "ClinicalCaseContext":
        meta = run_meta or ExecutionRunMetadata(case_id=str(raw_payload.get("patient", {}).get("id", "patient-a")))
        patient = raw_payload.get("patient", {})
        bb = BlackboardMemory()
        bb.write("patient_twin", patient)

        return cls(
            case_id=meta.case_id,
            run_id=meta.run_id,
            patient_twin=patient,
            inputs=raw_payload,
            blackboard=bb,
            idempotency_key=meta.idempotency_key,
            execution_status=PipelineState.INITIALIZING
        )

    def to_summary_dict(self) -> Dict[str, Any]:
        return {
            "case_id": self.case_id,
            "run_id": self.run_id,
            "execution_status": self.execution_status.value,
            "patient_id": self.patient_twin.get("id"),
            "patient_name": self.patient_twin.get("name"),
            "cancer_type": self.patient_twin.get("cancer_type"),
            "governance_status": self.governance_state.get("decision_status", "PENDING"),
            "events_recorded": len(self.provenance_trail),
            "created_at": self.created_at
        }
