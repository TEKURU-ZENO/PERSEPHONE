from backend.python.compute.ai_runtime.providers.mock import MockLLMProvider
from backend.python.compute.ai_runtime.providers.gemini import GeminiLLMProvider
from backend.python.compute.ai_runtime.providers.openai import OpenAILLMProvider
from backend.python.compute.ai_runtime.providers.anthropic import AnthropicLLMProvider
from backend.python.compute.ai_runtime.providers.deepseek import DeepSeekLLMProvider
from backend.python.compute.ai_runtime.providers.ollama import OllamaLLMProvider

class ProviderRegistry:
  """
  Registry mapping LLM names to concrete client implementations.
  """
  _ACTIVE_PROVIDER = "mock"
  _KEYS = {
    "gemini": None,
    "openai": None,
    "anthropic": None,
    "deepseek": None
  }

  @classmethod
  def set_active_provider(cls, name):
    cls._ACTIVE_PROVIDER = name

  @classmethod
  def get_active_provider_name(cls):
    return cls._ACTIVE_PROVIDER

  @classmethod
  def set_api_key(cls, name, key):
    if name in cls._KEYS:
      cls._KEYS[name] = key

  @classmethod
  def get_api_key(cls, name):
    return cls._KEYS.get(name)

  @classmethod
  def get_provider(cls, name=None):
    provider_name = name or cls._ACTIVE_PROVIDER
    
    if provider_name == "gemini":
      return GeminiLLMProvider(api_key=cls._KEYS.get("gemini"))
    elif provider_name == "openai":
      return OpenAILLMProvider(api_key=cls._KEYS.get("openai"))
    elif provider_name == "anthropic":
      return AnthropicLLMProvider(api_key=cls._KEYS.get("anthropic"))
    elif provider_name == "deepseek":
      return DeepSeekLLMProvider(api_key=cls._KEYS.get("deepseek"))
    elif provider_name == "ollama":
      return OllamaLLMProvider()
    
    return MockLLMProvider()
