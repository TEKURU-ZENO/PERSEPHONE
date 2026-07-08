class BaseLLMProvider:
  """
  Abstract Base Class interface for all Clinical AI Runtime (CAIR) providers.
  """
  def __init__(self, name):
    self.name = name

  def generate_completion(self, prompt, system_instruction=None, options=None):
    """
    Generates text completions for a prompt, returning a raw text string.
    """
    raise NotImplementedError

  def generate_embeddings(self, text):
    """
    Generates float vector embeddings for semantic matches.
    """
    raise NotImplementedError
