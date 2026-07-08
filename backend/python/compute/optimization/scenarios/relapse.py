def get_relapse_scenario():
  return {
    "duration": 180,
    "initialResistantRatio": 5.0,
    "alpha2": 0.055, # Elevated growth of resistant clones
    "mtdDose": 10.0,
    "dosingInterval": 7
  }
