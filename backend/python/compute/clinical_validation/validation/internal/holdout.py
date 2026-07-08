def split_validation_holdout(dataset, test_ratio=0.3):
  """
  Partitions empirical observations into training and testing blocks.
  """
  n = len(dataset)
  split_idx = int(n * (1.0 - test_ratio))
  return dataset[:split_idx], dataset[split_idx:]
