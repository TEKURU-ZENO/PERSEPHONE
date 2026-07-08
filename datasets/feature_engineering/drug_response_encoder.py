# Drug Response Feature Encoder
# Encodes IC50 parameters and categorizes drug sensitivity classes

def classify_sensitivity(ic50_value):
  """
  Categorizes IC50 response profiles:
  - Highly Sensitive: < 0.1 uM
  - Sensitive: < 1.0 uM
  - Resistant: >= 1.0 uM
  """
  try:
    val = float(ic50_value)
    if val < 0.1:
      return "Highly Sensitive"
    elif val < 1.0:
      return "Sensitive"
    else:
      return "Resistant"
  except ValueError:
    return "Unknown"

def process_drug_sensitivities(gdsc_records):
  """
  Processes and groups GDSC raw rows by cell line.
  """
  results = {}
  for r in gdsc_records:
    line_id = r.get('cellLineId')
    drug = r.get('drugName')
    ic50 = r.get('ic50_micromolar')

    if not line_id or not drug:
      continue

    if line_id not in results:
      results[line_id] = {}

    try:
      val = float(ic50)
      results[line_id][drug] = {
        "ic50": round(val, 4),
        "class": classify_sensitivity(val)
      }
    except ValueError:
      continue
  return results
