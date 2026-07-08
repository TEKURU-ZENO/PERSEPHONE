# Model specs database and capability indexer
MODELS_CATALOG = {
  "gemini-1.5-pro": {
    "provider": "gemini",
    "capabilities": ["vision", "long_context", "json_mode", "embeddings"],
    "maxContextTokens": 1000000,
    "inputPricePerMillion": 7.00,
    "outputPricePerMillion": 21.00
  },
  "gpt-4o": {
    "provider": "openai",
    "capabilities": ["vision", "structured_outputs", "json_mode", "embeddings"],
    "maxContextTokens": 128000,
    "inputPricePerMillion": 5.00,
    "outputPricePerMillion": 15.00
  },
  "claude-3-5-sonnet-20240620": {
    "provider": "anthropic",
    "capabilities": ["long_context", "reasoning", "pdf_mode"],
    "maxContextTokens": 200000,
    "inputPricePerMillion": 3.00,
    "outputPricePerMillion": 15.00
  },
  "deepseek-chat": {
    "provider": "deepseek",
    "capabilities": ["reasoning", "json_mode"],
    "maxContextTokens": 64000,
    "inputPricePerMillion": 0.14,
    "outputPricePerMillion": 0.28
  },
  "llama3": {
    "provider": "ollama",
    "capabilities": ["local_mode"],
    "maxContextTokens": 8000,
    "inputPricePerMillion": 0.00,
    "outputPricePerMillion": 0.00
  },
  "mock": {
    "provider": "mock",
    "capabilities": ["json_mode", "embeddings"],
    "maxContextTokens": 16000,
    "inputPricePerMillion": 0.00,
    "outputPricePerMillion": 0.00
  }
}

def check_model_capability(model_name, capability):
  model = MODELS_CATALOG.get(model_name, MODELS_CATALOG["mock"])
  return capability in model["capabilities"]
