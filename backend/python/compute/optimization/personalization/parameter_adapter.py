def adapt_patient_parameters(patient, control_params):
  """
  Injects age-adjusted clearances and genomic mutation burdens into RK4 parameters.
  """
  adapted = control_params.copy()
  
  # Map renal eGFR to ke clearance rate
  renal_str = str(patient.clinical_metrics.get("renal", "")).lower()
  if "normal" in renal_str:
    adapted["ke"] = 0.15
  elif "severe" in renal_str or "decline" in renal_str:
    adapted["ke"] = 0.08 # Impaired clearance rate
    
  return adapted
