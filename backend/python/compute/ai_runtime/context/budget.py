class ContextBudgetManager:
  """
  Allocates context window allocations dynamically across text sections.
  """
  def __init__(self, max_tokens=16000):
    self.max_tokens = max_tokens
    # 1 token ~= 4 characters as a baseline rule of thumb
    self.char_budget = max_tokens * 4

  def allocate_and_compress(self, sections):
    """
    Given sections dictionary (e.g. {"papers": "...", "patient": "..."}),
    truncates sections to fit within token budgets.
    """
    total_sections = len(sections)
    if total_sections == 0:
      return {}

    # Equal allocation per section
    char_limit_per_section = int(self.char_budget / total_sections)
    compressed = {}
    
    for section_name, text in sections.items():
      raw_text = str(text)
      if len(raw_text) > char_limit_per_section:
        compressed[section_name] = raw_text[:char_limit_per_section] + "\n... [TRUNCATED BY BUDGET MANAGER] ..."
      else:
        compressed[section_name] = raw_text
        
    return compressed
