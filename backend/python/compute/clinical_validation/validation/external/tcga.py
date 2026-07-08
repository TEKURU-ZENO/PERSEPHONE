def load_external_cohort_tcga(cohort_id="TCGA-OV"):
  """
  Placeholder loader for real-world TCGA/METABRIC datasets.
  """
  # Return representative ovarian metadata
  return {
    "cohort": cohort_id,
    "variantsDistribution": {"BRCA1": 0.18, "TP53": 0.94},
    "medianTTPDays": 114.5
  }
