import json
from backend.python.compute.ai_runtime.providers.base import BaseLLMProvider

class MockLLMProvider(BaseLLMProvider):
  """
  Mock provider returning structured outcomes for validation trials.
  """
  def __init__(self):
    super().__init__("mock")

  def generate_completion(self, prompt, system_instruction=None, options=None):
    # If the caller requests JSON structure, return a valid JSON string
    if "json" in str(prompt).lower() or "schema" in str(prompt).lower() or (options and options.get("response_format") == "json"):
      return json.dumps({
        "status": "success",
        "recommendation": "Mock Targeted Olaparib Dosing",
        "rationale": "Patient variants BRCA1 HGVSc mutation aligns with target indices.",
        "confidence": 0.94
      })
    return "Mock clinical completion response."

  def generate_embeddings(self, text):
    return [0.1] * 128
