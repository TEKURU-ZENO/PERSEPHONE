import time

class BaseClinicalAgent:
  """
  Abstract Base Class interface enforcing standard agent lifecycle hooks.
  """
  def __init__(self, name, classification):
    self.name = name
    self.classification = classification
    self.confidence = 0.90
    self.execution_time_ms = 0.0
    self.data_sources = []
    self.errors = None

  def initialize(self, blackboard):
    """
    Sets up dependencies and loads patient state details from blackboard.
    """
    pass

  def plan(self, blackboard):
    """
    Formulates tasks and execution dependencies.
    """
    pass

  def execute(self, blackboard):
    """
    Invokes numerical skills or queries generative models.
    """
    raise NotImplementedError

  def reflect(self, blackboard):
    """
    Checks constraints, self-corrects results, and validates limits.
    """
    pass

  def publish(self, blackboard):
    """
    Writes completed outcomes to the central Blackboard registry.
    """
    raise NotImplementedError

  def run_lifecycle(self, blackboard):
    start = time.perf_counter()
    try:
      self.initialize(blackboard)
      self.plan(blackboard)
      self.execute(blackboard)
      self.reflect(blackboard)
      self.publish(blackboard)
    except Exception as err:
      self.errors = str(err)
      raise err
    finally:
      self.execution_time_ms = (time.perf_counter() - start) * 1000.0
