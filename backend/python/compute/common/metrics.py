import time
import os

def profile_compute(start_time, algorithm="Numeric", additional_metadata=None):
  """
  Compiles SCR execution performance profiling measurements.
  """
  elapsed = (time.perf_counter() - start_time) * 1000.0 # convert to ms
  
  meta = {
    "runtime": "SCR",
    "version": "1.0",
    "executionTimeMs": round(elapsed, 3),
    "algorithm": algorithm
  }
  
  if additional_metadata:
    meta.update(additional_metadata)
    
  return meta
