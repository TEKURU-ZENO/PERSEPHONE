# Kaplan-Meier Survival Curve Encoder
# Calculates empirical survival distributions for patient cohorts

def compute_kaplan_meier(patient_records):
  """
  Computes survival curves over predefined time points (0, 180, 360, 540, 720, 900 days).
  """
  events = []
  for r in patient_records:
    try:
      days = float(r.get('survival_days', 0))
      deceased = r.get('vital_status', '').strip().lower() == 'deceased'
      events.append((days, deceased))
    except ValueError:
      continue

  if not events:
    return []

  # Sort by time
  events.sort(key=lambda x: x[0])
  
  time_points = [0.0, 180.0, 360.0, 540.0, 720.0, 900.0]
  survival_curve = []
  
  current_survival = 1.0
  n_at_risk = len(events)

  for tp in time_points:
    # Count deaths and censorings before or at this time point since the last time point
    # In a simplified KM step:
    deaths = 0
    censored = 0
    
    # We find deaths and censoring events occurring in this window
    for days, deceased in events:
      if days <= tp:
        if deceased:
          deaths += 1
        else:
          censored += 1
    
    # Simple cohort survival fraction
    total_deaths = sum(1 for days, deceased in events if days <= tp and deceased)
    total_censored = sum(1 for days, deceased in events if days <= tp and not deceased)
    
    # Active risk ratio
    at_risk = len(events) - sum(1 for days, deceased in events if days < tp)
    if at_risk > 0:
      # Simple fraction remaining alive
      alive = sum(1 for days, deceased in events if days > tp or (days == tp and not deceased))
      current_survival = round(alive / len(events), 4)
    else:
      current_survival = 0.0

    if tp == 0.0:
      current_survival = 1.0

    survival_curve.append({
      "timeDays": tp,
      "survivalRate": current_survival
    })
    
  return survival_curve
