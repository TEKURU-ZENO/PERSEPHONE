import json
import urllib.request
from backend.python.compute.ai_runtime.providers.base import BaseLLMProvider

class OllamaLLMProvider(BaseLLMProvider):
  """
  Local Ollama server provider client.
  """
  def __init__(self, endpoint="http://localhost:11434", model="llama3"):
    super().__init__("ollama")
    self.endpoint = endpoint
    self.model = model

  def generate_completion(self, prompt, system_instruction=None, options=None):
    url = f"{self.endpoint}/api/generate"
    
    payload = {
      "model": self.model,
      "prompt": prompt,
      "stream": False
    }
    if system_instruction:
      payload["system"] = system_instruction
      
    data = json.dumps(payload).encode("utf-8")
    
    req = urllib.request.Request(
      url, 
      data=data, 
      headers={"Content-Type": "application/json"}
    )
    
    try:
      with urllib.request.urlopen(req, timeout=10) as response:
        res_data = json.loads(response.read().decode())
        return res_data["response"]
    except Exception as err:
      return json.dumps({"error": f"Ollama request failed: {str(err)}"})

  def generate_embeddings(self, text):
    return [0.02] * 128
