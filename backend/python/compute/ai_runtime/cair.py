import time
from backend.python.compute.ai_runtime.registry.providers import ProviderRegistry
from backend.python.compute.ai_runtime.router.router import ModelRouter
from backend.python.compute.ai_runtime.context.budget import ContextBudgetManager
from backend.python.compute.ai_runtime.middleware.retry import execute_with_retry
from backend.python.compute.ai_runtime.output.parser import parse_structured_json
from backend.python.compute.ai_runtime.observability.metrics import TokenAccountingTelemetry

class ClinicalAIRuntime:
  """
  Clinical AI Runtime (CAIR) core coordinator orchestrating multi-LLM workflows.
  """
  @staticmethod
  def generate_structured_response(prompt, capability="json_mode", system_instruction=None):
    start = time.perf_counter()
    
    # 1. Model routing
    model_name, provider_name = ModelRouter.route_by_capability(capability)
    
    # 2. Context budget management
    budget_manager = ContextBudgetManager(max_tokens=16000)
    compressed_sections = budget_manager.allocate_and_compress({"prompt": prompt})
    final_prompt = compressed_sections["prompt"]

    # 3. Provider resolution
    provider = ProviderRegistry.get_provider(provider_name)
    
    # 4. Middleware: execute with retry
    call_fn = lambda: provider.generate_completion(
      final_prompt, 
      system_instruction=system_instruction,
      options={"response_format": "json"}
    )
    
    raw_completion = execute_with_retry(call_fn)
    latency_ms = (time.perf_counter() - start) * 1000.0

    # 5. Output parser structured JSON
    structured_json = parse_structured_json(raw_completion)

    # 6. Observability token logs
    TokenAccountingTelemetry.record_transaction(
      model_name, 
      final_prompt, 
      raw_completion, 
      latency_ms
    )

    return structured_json
