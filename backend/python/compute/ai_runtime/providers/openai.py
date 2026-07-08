import json
import urllib.request
from backend.python.compute.ai_runtime.providers.base import BaseLLMProvider

class OpenAILLMProvider(BaseLLMProvider):
  """
  OpenAI GPT API provider client.
  """
  def __init__(self, api_key=None, model="gpt-4o"):
    super().__init__("openai")
    self.api_key = api_key
    self.model = model

  def generate_completion(self, prompt, system_instruction=None, options=None):
    if not self.api_key:
      return json.dumps({"error": "Missing OpenAI API key"})

    url = "https://api.openai.com/v1/chat/completions"
    
    messages = []
    if system_instruction:
      messages.append({"role": "system", "content": system_instruction})
    messages.append({"role": "user", "content": prompt})
    
    payload = {
      "model": self.model,
      "messages": messages
    }
    
    data = json.dumps(payload).encode("utf-8")
    
    req = urllib.request.Request(
      url, 
      data=data, 
      headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {self.api_key}"
      }
    )
    
    try:
      with urllib.request.urlopen(req, timeout=10) as response:
        res_data = json.loads(response.read().decode())
        return res_data["choices"][0]["message"]["content"]
    except Exception as err:
      return json.dumps({"error": f"OpenAI API request failed: {str(err)}"})

  def generate_embeddings(self, text):
    return [0.08] * 128
