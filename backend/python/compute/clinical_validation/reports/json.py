import json

def export_json_report(fit_results, fit_metrics, sens_results, ablation_results):
  return {
    "calibration": fit_results,
    "goodnessOfFit": fit_metrics,
    "sensitivity": sens_results,
    "ablation": ablation_results
  }
