def get_reward_breakdown(total_volume, toxicity, is_alive, is_dosing):
  return {
    "tumorPenalties": -0.05 * total_volume,
    "toxicityPenalties": -10.0 * max(0.0, toxicity - 0.50),
    "survivalBonuses": 1.5 if (is_alive and not is_dosing) else 1.0 if is_alive else 0.0
  }
