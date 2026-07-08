def calculate_prediction_intervals(timeline):
  """
  Calculates width of prediction bands.
  """
  widths = []
  for pt in timeline:
    widths.append(pt["upper"] - pt["lower"])
  return {
    "averageWidth": round(sum(widths) / len(widths) if widths else 0.0, 3)
  }
