import unittest
from backend.python.compute.ai_runtime.registry.models import check_model_capability
from backend.python.compute.ai_runtime.registry.providers import ProviderRegistry
from backend.python.compute.ai_runtime.router.router import ModelRouter
from backend.python.compute.ai_runtime.context.budget import ContextBudgetManager
from backend.python.compute.ai_runtime.output.parser import parse_structured_json
from backend.python.compute.ai_runtime.observability.metrics import TokenAccountingTelemetry

class TestClinicalAIRuntime(unittest.TestCase):
  def test_model_capabilities(self):
    self.assertTrue(check_model_capability("gpt-4o", "structured_outputs"))
    self.assertFalse(check_model_capability("llama3", "vision"))

  def test_model_router_policy(self):
    # Route for vision (should yield gemini or openai if configured/mock fallback)
    model, provider = ModelRouter.route_by_capability("vision")
    self.assertTrue(provider in ["gemini", "openai", "mock"])

  def test_context_budget_compressor(self):
    # 1 token = 4 chars. budget = 10 tokens (40 chars)
    manager = ContextBudgetManager(max_tokens=10)
    sections = {
      "patient": "A very long longitudinal oncology digital twin patient profile description."
    }
    compressed = manager.allocate_and_compress(sections)
    self.assertTrue(len(compressed["patient"]) <= 90) # 40 chars + truncation string
    self.assertTrue("TRUNCATED" in compressed["patient"])

  def test_structured_json_parser_and_repair(self):
    raw_markdown = "```json\n{\"recommendation\": \"dosing\"}\n```"
    parsed = parse_structured_json(raw_markdown)
    self.assertEqual(parsed["recommendation"], "dosing")

    # Repair unclosed brace
    raw_broken = "{\"recommendation\": \"dosing\""
    parsed_broken = parse_structured_json(raw_broken)
    self.assertEqual(parsed_broken["recommendation"], "dosing")

  def test_token_cost_telemetry(self):
    TokenAccountingTelemetry.record_transaction(
      "gpt-4o",
      "Explain pathway",
      "Recommendation targeted Olaparib.",
      latency_ms=150.0
    )
    summary = TokenAccountingTelemetry.get_accumulated_summary()
    self.assertEqual(summary["totalCalls"], 1)
    self.assertTrue(summary["totalTokens"] > 0)
    self.assertTrue(summary["totalCostUsd"] > 0)

if __name__ == '__main__':
  unittest.main()
