from backend.python.compute.ai_runtime.registry.models import check_model_capability, MODELS_CATALOG
from backend.python.compute.ai_runtime.registry.providers import ProviderRegistry

class ModelRouter:
  """
  Routes queries to models based on task capability requirements.
  """
  @staticmethod
  def route_by_capability(required_capability):
    # Scan catalog for models matching capability
    for model_name, spec in MODELS_CATALOG.items():
      if check_model_capability(model_name, required_capability):
        # Verify if api-key exists for the provider
        provider_name = spec["provider"]
        if provider_name == "mock" or provider_name == "ollama" or ProviderRegistry.get_api_key(provider_name):
          return model_name, provider_name
          
    # Fallback to active registry settings
    active = ProviderRegistry.get_active_provider_name()
    return "active-model", active
