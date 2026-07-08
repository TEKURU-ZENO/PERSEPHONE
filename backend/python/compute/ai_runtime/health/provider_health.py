import time
from backend.python.compute.ai_runtime.registry.providers import ProviderRegistry

class ProviderHealthMonitor:
  """
  Monitors provider api-key statuses and query latencies.
  """
  _STATUS_CACHE = {}

  @classmethod
  def ping_provider(cls, name):
    start = time.perf_counter()
    provider = ProviderRegistry.get_provider(name)
    
    # Run a simple completion ping
    try:
      res = provider.generate_completion("ping")
      latency = (time.perf_counter() - start) * 1000.0
      
      status = {
        "status": "online" if "error" not in str(res).lower() else "degraded",
        "latencyMs": round(latency, 2),
        "lastSuccess": time.strftime("%Y-%m-%d %H:%M:%S"),
        "lastError": None
      }
    except Exception as err:
      status = {
        "status": "offline",
        "latencyMs": 999.0,
        "lastSuccess": None,
        "lastError": str(err)
      }
      
    cls._STATUS_CACHE[name] = status
    return status

  @classmethod
  def get_health_report(cls):
    # Check all active credentials
    report = {}
    for name in ["gemini", "openai", "anthropic", "deepseek", "ollama", "mock"]:
      if name in cls._STATUS_CACHE:
        report[name] = cls._STATUS_CACHE[name]
      else:
        # Default fallback
        has_key = ProviderRegistry.get_api_key(name) is not None or name in ["mock", "ollama"]
        report[name] = {
          "status": "online" if has_key else "offline",
          "latencyMs": 0.0,
          "lastSuccess": None,
          "lastError": None if has_key else "Missing credentials API Key"
        }
    return report
