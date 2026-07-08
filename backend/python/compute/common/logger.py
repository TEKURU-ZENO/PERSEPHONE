import logging
import os
import sys
from backend.python.config.logging import LOG_FILE, LOG_FORMAT, LOG_LEVEL

def setup_logger(name="SCR"):
  logger = logging.getLogger(name)
  if logger.hasHandlers():
    return logger

  logger.setLevel(LOG_LEVEL)
  
  formatter = logging.Formatter(LOG_FORMAT)

  # Console handler
  console = logging.StreamHandler(sys.stdout)
  console.setFormatter(formatter)
  logger.addHandler(console)

  # File handler
  try:
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
  except Exception as e:
    print(f"Warning: Failed to create log file handler: {e}")

  return logger

# Export default logger
logger = setup_logger("SCR_Core")
