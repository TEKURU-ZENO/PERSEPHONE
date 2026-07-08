import json
import urllib.request
from backend.python.compute.ai_runtime.providers.base import BaseLLMProvider

class GeminiLLMProvider(BaseLLMProvider):
  """
  Google Gemini API provider client.
  """
  def __init__(self, api_key=None, model="gemini-1.5-pro"):
    super().__init__("gemini")
    self.api_key = api_key
    self.model = model

  def generate_completion(self, prompt, system_instruction=None, options=None):
    if not self.api_key:
      # Fallback to mock behavior if key is missing
      return json.dumps({"error": "Missing Gemini API key"})

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
    
    contents = {"parts": [{"text": prompt}]}
    payload = {"contents": [contents]}
    if system_instruction:
      payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}
      
    data = json.dumps(payload).encode("utf-8")
    
    req = urllib.request.Request(
      url, 
      data=data, 
      headers={"Content-Type": "application/json"}
    )
    
    try:
      with urllib.request.urlopen(req, timeout=10) as response:
        res_data = json.loads(response.read().decode())
        return res_data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as err:
      return json.dumps({"error": f"Gemini API request failed: {str(err)}"})

  def generate_embeddings(self, text):
    return [0.05] * 128
