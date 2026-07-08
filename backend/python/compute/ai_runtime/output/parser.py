import re
import json
from backend.python.compute.common.logger import logger

def parse_structured_json(raw_text):
  """
  Extracts and parses JSON structures from raw LLM text outputs, repairing fences and brackets.
  """
  clean = raw_text.strip()
  
  # Remove markdown code fences if present
  if clean.startswith("```"):
    clean = re.sub(r"^```[a-zA-Z]*\n", "", clean)
    clean = re.sub(r"\n```$", "", clean)
    clean = clean.strip()
    
  # Simple auto-repair for unclosed brackets
  if clean.startswith("{") and not clean.endswith("}"):
    logger.warning("CAIR: Unclosed JSON object detected. Appending closing brace.")
    clean += "}"
  elif clean.startswith("[") and not clean.endswith("]"):
    logger.warning("CAIR: Unclosed JSON array detected. Appending closing bracket.")
    clean += "]"

  try:
    return json.loads(clean)
  except Exception as err:
    # Attempt regex capture
    json_match = re.search(r"(\{.*\}|\[.*\])", clean, re.DOTALL)
    if json_match:
      try:
        return json.loads(json_match.group(1))
      except Exception:
        pass
    logger.error(f"CAIR: JSON parsing failed: {str(err)}. Raw text: {raw_text}")
    raise ValueError(f"Invalid structured JSON format output: {str(err)}")
