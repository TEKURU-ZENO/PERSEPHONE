# Graph-RAG Vector Search Engine
from backend.python.config.datasets import LITERATURE_DATABASE, embed_query_text

def dot_product(v1, v2):
  return sum(v1[i] * v2[i] for i in range(len(v1)))

def magnitude(v):
  return sum(x*x for x in v) ** 0.5

def calculate_cosine_similarity(v1, v2):
  mag1 = magnitude(v1)
  mag2 = magnitude(v2)
  if mag1 == 0 or mag2 == 0:
    return 0.0
  return dot_product(v1, v2) / (mag1 * mag2)

def search_literature(query_text, threshold=0.1):
  """
  Performs Cosine Similarity search over cached publications.
  """
  query_vec = embed_query_text(query_text)
  results = []
  
  for paper in LITERATURE_DATABASE:
    sim = calculate_cosine_similarity(query_vec, paper["vector"])
    if sim >= threshold:
      # Return copy with score
      paper_copy = paper.copy()
      paper_copy["cosineSimilarity"] = round(sim, 4)
      results.append(paper_copy)

  # Sort descending by score
  results.sort(key=lambda x: x["cosineSimilarity"], reverse=True)
  return results
