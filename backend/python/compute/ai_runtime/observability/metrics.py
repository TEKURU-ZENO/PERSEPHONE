from backend.python.compute.ai_runtime.registry.models import MODELS_CATALOG

class TokenAccountingTelemetry:
  """
  Telemetry logs accounting token volumes and API costs.
  """
  _LOGS = []

  @classmethod
  def estimate_tokens(cls, text):
    """
    Standard token volume estimator (1 token ~= 4 chars).
    """
    return max(1, int(len(str(text)) / 4))

  @classmethod
  def record_transaction(cls, model_name, prompt, completion, latency_ms):
    p_tokens = cls.estimate_tokens(prompt)
    c_tokens = cls.estimate_tokens(completion)
    
    # Lookup model prices
    spec = MODELS_CATALOG.get(model_name, MODELS_CATALOG["mock"])
    input_price = spec["inputPricePerMillion"]
    output_price = spec["outputPricePerMillion"]
    
    cost = ((p_tokens * input_price) + (c_tokens * output_price)) / 1000000.0
    
    log_entry = {
      "model": model_name,
      "promptTokens": p_tokens,
      "completionTokens": c_tokens,
      "costUsd": round(cost, 6),
      "latencyMs": round(latency_ms, 2)
    }
    
    cls._LOGS.append(log_entry)
    return log_entry

  @classmethod
  def get_accumulated_summary(cls):
    total_cost = sum(l["costUsd"] for l in cls._LOGS)
    total_tokens = sum(l["promptTokens"] + l["completionTokens"] for l in cls._LOGS)
    
    return {
      "totalCalls": len(cls._LOGS),
      "totalTokens": total_tokens,
      "totalCostUsd": round(total_cost, 6),
      "recentLogs": cls._LOGS[-5:]
    }
