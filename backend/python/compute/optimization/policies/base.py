class BasePolicy:
  """
  Abstract Base Class interface for all pluggable clinical policies.
  """
  def __init__(self, name):
    self.name = name

  def select_action(self, state):
    """
    Given a 6D environment state observation, returns action index in [0, 4].
    """
    raise NotImplementedError
