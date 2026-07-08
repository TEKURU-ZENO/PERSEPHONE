import time
from backend.python.compute.common.logger import logger

def execute_with_retry(fn, retries=3, delay=1.0):
  """
  Executes a provider completion call with transient error retries.
  """
  last_err = None
  for attempt in range(retries):
    try:
      return fn()
    except Exception as err:
      last_err = err
      logger.warning(f"CAIR: Call attempt {attempt + 1} failed: {str(err)}. Retrying in {delay}s...")
      time.sleep(delay)
      delay *= 2.0
      
  logger.error(f"CAIR: All {retries} retries exhausted. Exception: {str(last_err)}")
  raise last_err
