def trace_constraints(toxicity, egfr_val):
  trace = []
  if toxicity > 0.50:
    trace.append(f"Toxicity elevated at {toxicity:.2f} (Warning threshold 0.50)")
  if egfr_val < 60:
    trace.append(f"Impaired clearance (eGFR: {egfr_val} mL/min/1.73m²)")
  return trace
