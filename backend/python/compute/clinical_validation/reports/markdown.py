def generate_validation_markdown_report(patient, fit_results, fit_metrics, sens_results):
  lines = [
    "# SCIENTIFIC VALIDATION AND CALIBRATION REPORT",
    f"**Patient Twin ID:** {patient.patient_id}",
    f"**Diagnosis:** {patient.diagnosis}",
    "",
    "## 1. Parameters Fit (L-BFGS-B Optimization)",
    "| Parameter | Calibrated Value | Initial Prior |",
    "|---|---|---|",
    f"| K (Carrying Capacity) | {fit_results['calibratedParams']['K']} | 200.0 |",
    f"| alpha1 (Sensitive Growth) | {fit_results['calibratedParams']['alpha1']} | 0.0800 |",
    f"| alpha2 (Resistant Growth) | {fit_results['calibratedParams']['alpha2']} | 0.0450 |",
    "",
    "## 2. Goodness-of-Fit Validation Statistics",
    f"- **Root Mean Squared Error (RMSE):** {fit_metrics['rmse']}",
    f"- **Mean Absolute Error (MAE):** {fit_metrics['mae']}",
    f"- **Coefficient of Determination (R²):** {fit_metrics['r2']}",
    f"- **AIC / BIC Information Criteria:** {fit_metrics['aic']} / {fit_metrics['bic']}",
    f"- **Trend Concordance Index:** {fit_metrics['concordanceIndex']}%",
    "",
    "## 3. Parameter Sensitivity Contributions",
  ]
  
  for param, sens in sens_results.items():
    lines.append(f"- **{param}:** {sens}% contribution")
    
  return "\n".join(lines)
