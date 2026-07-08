def generate_optimization_report(comparison_results):
  """
  Compiles markdown summaries of comparative policy benchmarks.
  """
  lines = [
    "# CLINICAL POLICY BENCHMARK LEADERBOARD REPORT",
    "",
    "| Policy | Tumor Control | PFS | Toxicity Margin | Quality of Life | Resistance Suppression | Overall Score |",
    "|---|---|---|---|---|---|---|",
  ]
  
  for policy, data in comparison_results.items():
    m = data["metrics"]
    lines.append(
      f"| **{policy.upper()}** | {m['tumorControl']}% | {m['pfs']}% | {m['toxicityProfile']}% | {m['qualityOfLife']}% | {m['resistanceSuppression']}% | **{m['overallScore']}** |"
    )
    
  return "\n".join(lines)
