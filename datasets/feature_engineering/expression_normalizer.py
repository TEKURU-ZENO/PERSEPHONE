# Gene Expression Normalizer
# Implements standard log2(TPM + 1) normalization transforms for molecular profiles

import math

def log2_transform(value):
  """
  Computes log2(value + 1) to compress extreme reads variances.
  """
  try:
    val = float(value)
    if val < 0:
      return 0.0
    return round(math.log2(val + 1), 4)
  except ValueError:
    return 0.0

def normalize_expression_matrix(expression_records):
  """
  Processes and groups raw gene expression rows by cell line.
  """
  normalized = {}
  for r in expression_records:
    line_id = r.get('cellLineId')
    gene = r.get('gene')
    expr_raw = r.get('expression_level')

    if not line_id or not gene:
      continue

    if line_id not in normalized:
      normalized[line_id] = {}

    normalized[line_id][gene] = log2_transform(expr_raw)
  return normalized
