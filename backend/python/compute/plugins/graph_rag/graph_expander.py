# Graph-RAG Graph Expander
from backend.python.compute.graph.pathfinding import build_graph

def expand_query_subgraph(parsed_entities):
  """
  Traverses the BKG to retrieve related nodes and edges matching parsed query terms.
  """
  nodes, edges = build_graph()
  
  target_ids = set()
  # Gather all parsed term canonical keys
  for cat in parsed_entities:
    for term in parsed_entities[cat]:
      target_ids.add(term.lower())
      target_ids.add(term) # Keep case for genes (e.g. BRCA1)

  active_nodes = set()
  active_edges = []

  # Find matches
  for node in nodes:
    nid = node["id"]
    if nid.lower() in target_ids or nid in target_ids:
      active_nodes.add(nid)

  # Traversal expansion (1-hop neighbors)
  for node_id in list(active_nodes):
    for edge in edges:
      if edge["source"] == node_id:
        active_nodes.add(edge["target"])
        active_edges.append(edge)
      elif edge["target"] == node_id:
        active_nodes.add(edge["source"])
        active_edges.append(edge)

  # Filter actual nodes
  node_map = {n["id"]: n for n in nodes}
  expanded_nodes = [node_map[id] for id in active_nodes if id in node_map]
  expanded_edges = [e for e in active_edges if e["source"] in node_map and e["target"] in node_map]

  return expanded_nodes, expanded_edges
