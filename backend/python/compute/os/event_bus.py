"""
OS Event Bus Module for PERSEPHONE OS.
Implements the in-memory reactive event stream ("What just happened?").
Maintains a rolling event log for live streaming to the OS Cockpit.
"""
from typing import Dict, List, Any, Callable
from collections import deque
import threading
from backend.python.compute.os.contracts.events import EventContract


class OSEventBus:
    """
    Reactive Event Bus for PERSEPHONE OS.
    Dispatches asynchronous state change events across planes and streams them to the UI.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(OSEventBus, cls).__new__(cls)
                cls._instance._subscribers = []
                cls._instance._event_log = deque(maxlen=2000)
            return cls._instance

    def subscribe(self, callback: Callable[[EventContract], None]):
        """Subscribes an observer callback to the event stream."""
        with self._lock:
            if callback not in self._subscribers:
                self._subscribers.append(callback)

    def publish_event(
        self,
        event_type: str,
        plane: Any,
        agent_name: str,
        payload: Dict[str, Any],
        run_id: str = "RUN-DEFAULT",
        parent_event_id: str = None
    ) -> EventContract:
        """Publishes an event and dispatches it to all subscribers."""
        plane_val = plane.value if hasattr(plane, 'value') else str(plane)
        event = EventContract(
            run_id=run_id,
            event_type=event_type,
            plane=plane_val,
            agent_name=agent_name,
            payload=payload,
            parent_event_id=parent_event_id
        )

        with self._lock:
            self._event_log.append(event)
            subs = list(self._subscribers)

        for sub in subs:
            try:
                sub(event)
            except Exception as err:
                pass  # Avoid subscriber exceptions from bubbling into kernel

        return event

    def emit(
        self,
        event_type: str,
        plane: Any,
        agent_name: str,
        payload: Dict[str, Any],
        run_id: str = "RUN-DEFAULT",
        parent_event_id: str = None
    ) -> EventContract:
        """Alias for publish_event."""
        return self.publish_event(
            event_type=event_type,
            plane=plane,
            agent_name=agent_name,
            payload=payload,
            run_id=run_id,
            parent_event_id=parent_event_id
        )

    def get_events(self, run_id: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieves recent events, optionally filtered by run_id."""
        with self._lock:
            events = list(self._event_log)

        if run_id:
            events = [e for e in events if e.run_id == run_id]

        return [e.to_dict() for e in events[-limit:]]

    def clear(self):
        """Clears in-memory event logs (useful for test isolation)."""
        with self._lock:
            self._event_log.clear()
