def verify_renal_clearance(clinical_metrics, dose_level):
  """
  Blocks full dosing if renal clearance eGFR indicates severe impairment.
  """
  renal_str = str(clinical_metrics.get("renal", "")).lower()
  
  if "severe" in renal_str or "decline" in renal_str:
    if dose_level > 0.5:
      return False, f"Renal clearance safety limit exceeded. Full dosing blocked due to impaired organ function."
  return True, None
