from backend.python.compute.optimization.clinical_objectives.tumor_control import evaluate_tumor_control
from backend.python.compute.optimization.clinical_objectives.survival import evaluate_progression_free_survival
from backend.python.compute.optimization.clinical_objectives.toxicity import evaluate_toxicity_profile
from backend.python.compute.optimization.clinical_objectives.quality_of_life import evaluate_quality_of_life
from backend.python.compute.optimization.clinical_objectives.resistance_delay import evaluate_resistance_suppression

def evaluate_trajectory_metrics(trajectory_output):
  """
  Compiles multidimensional scores for publication leaderboard comparisons.
  """
  timeline = trajectory_output.get("timeline", [])
  ttp = trajectory_output.get("timeToProgression", 180.0)

  tumor_ctrl = evaluate_tumor_control(timeline)
  pfs = evaluate_progression_free_survival(ttp)
  tox_profile = evaluate_toxicity_profile(timeline)
  qol = evaluate_quality_of_life(timeline)
  resistance = evaluate_resistance_suppression(timeline)

  # Composite score (average of metrics)
  overall_score = (tumor_ctrl + pfs + tox_profile + qol + resistance) / 5.0

  return {
    "tumorControl": round(tumor_ctrl, 1),
    "pfs": round(pfs, 1),
    "toxicityProfile": round(tox_profile, 1),
    "qualityOfLife": round(qol, 1),
    "resistanceSuppression": round(resistance, 1),
    "overallScore": round(overall_score, 1)
  }
