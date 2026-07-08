import time

class AgentEventBus:
  """
  Event bus routing clinical state updates and logging telemetry pings.
  """
  def __init__(self):
    self.events = []
    self.subscribers = []

  def publish_event(self, event_type, source, payload=None):
    event_entry = {
      "timestamp": time.time(),
      "eventType": event_type,
      "source": source,
      "payload": payload
    }
    self.events.append(event_entry)
    
    # Trigger active subscribers
    for sub_fn in self.subscribers:
      try:
        sub_fn(event_type, source, payload)
      except Exception:
        pass

  def subscribe(self, fn):
    self.subscribers.append(fn)

  def get_logs(self):
    return self.events
