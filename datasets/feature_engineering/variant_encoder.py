# Somatic Variant Feature Encoder
# Standardizes mutations and computes mutation frequencies

def encode_variants(raw_records):
  """
  Encodes variants list from patient records.
  """
  encoded = {}
  for r in raw_records:
    gene = r.get('mutation_gene')
    if not gene or gene == 'N/A':
      continue
    encoded[gene] = encoded.get(gene, 0) + 1
  
  # Calculate frequency ratios
  total = sum(encoded.values()) or 1
  return {
    "geneFrequencies": {k: round(v / total, 3) for k, v in encoded.items()},
    "mutatedGenes": list(encoded.keys())
  }
