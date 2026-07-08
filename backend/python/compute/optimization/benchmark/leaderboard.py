def compile_leaderboard(comparison_results):
  """
  Compiles sorted leaderboard entries based on overall scoring metrics.
  """
  entries = []
  for policy, data in comparison_results.items():
    m = data["metrics"]
    entries.append({
      "policy": policy,
      "overallScore": m["overallScore"],
      "tumorControl": m["tumorControl"],
      "pfs": m["pfs"],
      "qualityOfLife": m["qualityOfLife"]
    })
    
  # Sort descending by overall score
  entries.sort(key=lambda x: x["overallScore"], reverse=True)
  return entries
