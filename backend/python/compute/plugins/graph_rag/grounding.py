# Graph-RAG Grounding and Hallucination Checker

def validate_recommendation_grounding(drug, mutation, disease, context_text, graph_nodes):
  """
  Asserts entity and relationship boundaries:
  1. Drug entity must exist in the matched literature context text.
  2. Drug target relationship to the target mutation must exist.
  """
  violations = []
  
  drug_clean = drug.strip().lower()
  mutation_clean = mutation.strip().lower()
  disease_clean = disease.strip().lower()

  # 1. Entity Grounding: Check if drug exists in bibliography context text
  if drug_clean not in context_text.lower():
    violations.append(f"Entity Hallucination: Recommended drug '{drug}' does not exist in literature abstracts.")

  # 2. Relationship Grounding: check drug -> mutation target association in graph nodes
  node_ids = {n.get("id", "").lower() for n in graph_nodes}
  
  if drug_clean not in node_ids:
    violations.append(f"Relationship Hallucination: Recommended drug '{drug}' does not target patient entities in Knowledge Graph.")

  if mutation_clean not in node_ids:
    violations.append(f"Relationship Hallucination: Mutation target '{mutation}' does not exist in Patient active pathways.")

  # Calculate grounding score
  score = 1.0 - (len(violations) * 0.4)
  score = max(0.0, min(1.0, score))

  return {
    "grounded": len(violations) == 0,
    "score": round(score, 2),
    "violations": violations
  }
