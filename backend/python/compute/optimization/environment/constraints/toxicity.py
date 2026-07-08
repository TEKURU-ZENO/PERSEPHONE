def verify_toxicity_limit(toxicity, dose_level, max_allowed_toxicity=0.85):
  """
  Asserts that dosing is withheld if patient systemic toxicity is dangerously high.
  """
  if toxicity >= max_allowed_toxicity and dose_level > 0.0:
    return False, f"High toxicity limit violation ({toxicity:.2f} >= {max_allowed_toxicity}). Dosing must be suspended."
  return True, None
