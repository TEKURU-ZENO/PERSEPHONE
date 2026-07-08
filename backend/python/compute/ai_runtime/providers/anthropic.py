import json
import urllib.request
from backend.python.compute.ai_runtime.providers.base import BaseLLMProvider

class AnthropicLLMProvider(BaseLLMProvider):
  """
  Anthropic Claude API provider client.
  """
  def __init__(self, api_key=None, model="claude-3-5-sonnet-20240620"):
    super().__init__("anthropic")
    self.api_key = api_key
    self.model = model

  def generate_completion(self, prompt, system_instruction=None, options=None):
    if not self.api_key:
      return json.dumps({"error": "Missing Anthropic API key"})

    url = "https://api.anthropic.com/v1/messages"
    
    payload = {
      "model": self.model,
      "messages": [{"role": "user", "content": prompt}],
      "max_tokens": 1024
    }
    if system_instruction:
      payload["system"] = system_instruction
      
    data = json.dumps(payload).encode("utf-8")
    
    req = urllib.request.Request(
      url, 
      data=data, 
      headers={
        "Content-Type": "application/json",
        "x-api-key": self.api_key,
        "anthropic-version": "2023-06-01"
      }
    )
    
    try:
      with urllib.request.urlopen(req, timeout=10) as response:
        res_data = json.loads(response.read().decode())
        return res_data["content"][0]["text"]
    except Exception as err:
      return json.dumps({"error": f"Anthropic API request failed: {str(err)}"})

  def generate_embeddings(self, text):
    return [0.03] * 128
