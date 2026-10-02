"""
Event Contract Schema v1.0 for PERSEPHONE OS.
Standardizes reactive event payloads dispatched on OSEventBus.
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import time
import uuid


@dataclass
class EventContract:
    """Canonical event payload on the OS Event Bus."""
    event_id: str = field(default_factory=lambda: f"EVT-{int(time.time()*1000)}-{uuid.uuid4().hex[:6]}")
    run_id: str = "RUN-DEFAULT"
    event_type: str = "STATE_CHANGE"
    plane: str = "PATIENT_INTELLIGENCE"
    agent_name: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    parent_event_id: Optional[str] = None
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "run_id": self.run_id,
            "event_type": self.event_type,
            "plane": self.plane,
            "agent_name": self.agent_name,
            "payload": self.payload,
            "parent_event_id": self.parent_event_id,
            "timestamp": self.timestamp
        }
