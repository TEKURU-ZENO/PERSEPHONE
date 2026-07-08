# Graph-RAG Evidence Ranker and Citation Evaluator

def rank_publications(literature_results):
  """
  Calculates evidence weights and confidence metrics:
  Score = CosineSimilarity * 40 + RecencyWeight * 20 + JournalWeight * 20 + PhaseWeight * 20
  """
  ranked = []
  
  for paper in literature_results:
    sim = paper.get("cosineSimilarity", 0.0)
    
    # 1. Recency (20 points)
    year = paper.get("year", 2000)
    recency_score = 20.0 if year >= 2018 else 10.0
    
    # 2. Journal Rank (20 points)
    journal = paper.get("journal", "")
    journal_score = 20.0 if journal in ["Nature", "New England Journal of Medicine"] else 12.0

    # 3. Phase Strength (20 points)
    phase = paper.get("phase", "")
    phase_score = 20.0 if "Phase III" in phase or "Phase I/II" in phase else 10.0

    # 4. Similarity score (40 points max)
    similarity_contribution = sim * 40.0

    overall_score = round(similarity_contribution + recency_score + journal_score + phase_score, 1)

    paper_copy = paper.copy()
    paper_copy["evidenceScore"] = overall_score
    ranked.append(paper_copy)

  # Sort descending by evidence score
  return sorted(ranked, key=lambda x: x["evidenceScore"], reverse=True)
