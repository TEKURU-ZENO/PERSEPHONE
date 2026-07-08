import numpy as np

def calculate_goodness_of_fit(observed, simulated):
  """
  Computes clinical metrics evaluating modeling fits.
  """
  obs = np.array(observed, dtype=np.float64)
  sim = np.array(simulated, dtype=np.float64)

  if len(obs) == 0:
    return {}

  # Residual errors
  residuals = obs - sim
  rmse = np.sqrt(np.mean(residuals ** 2))
  mae = np.mean(np.abs(residuals))
  mape = np.mean(np.abs(residuals) / np.maximum(obs, 1e-5)) * 100.0

  # R-squared calculation
  mean_obs = np.mean(obs)
  total_ss = np.sum((obs - mean_obs) ** 2)
  residual_ss = np.sum(residuals ** 2)
  r2 = 1.0 - (residual_ss / total_ss) if total_ss > 0 else 0.0

  # Akaike & Bayesian Information Criteria (AIC/BIC)
  n = len(obs)
  k = 3 # Number of fitted variables [K, a1, a2]
  rss = np.sum(residuals ** 2)
  
  if rss > 0:
    aic = n * np.log(rss / n) + 2 * k
    bic = n * np.log(rss / n) + k * np.log(n)
  else:
    aic = -999.0
    bic = -999.0

  # Simple Concordance Index mapping trend alignments
  concordant = 0
  total_pairs = 0
  for i in range(len(obs)):
    for j in range(i + 1, len(obs)):
      obs_trend = obs[i] - obs[j]
      sim_trend = sim[i] - sim[j]
      if (obs_trend * sim_trend) > 0:
        concordant += 1
      total_pairs += 1
  c_index = (concordant / total_pairs) * 100.0 if total_pairs > 0 else 100.0

  return {
    "rmse": round(float(rmse), 4),
    "mae": round(float(mae), 4),
    "r2": round(float(r2), 4),
    "mape": round(float(mape), 2),
    "aic": round(float(aic), 2),
    "bic": round(float(bic), 2),
    "concordanceIndex": round(float(c_index), 2)
  }
