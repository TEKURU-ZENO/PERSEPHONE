def get_metastatic_scenario():
  return {
    "duration": 180,
    "initialResistantRatio": 8.0,
    "K": 120.0, # Lower carrying capacity (niche spatial constraint)
    "mtdDose": 10.0,
    "dosingInterval": 7
  }
