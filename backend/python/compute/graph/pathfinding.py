# Causal Pathfinding Graph Algorithm
import os
import json

def get_mutation_id(name):
  upper_name = name.upper()
  if 'C.1961DELA' in upper_name or 'BRCA1-MUT' in upper_name:
    return 'brca1-mut'
  if 'L858R' in upper_name or 'C.2573T>G' in upper_name:
    return 'egfr-l858r'
  if 'T790M' in upper_name or 'C.2369C>T' in upper_name:
    return 'egfr-t790m'
  if 'MET' in upper_name and ('AMPLIFICATION' in upper_name or 'COPY GAIN' in upper_name):
    return 'met-amp'
  if 'G12D' in upper_name or 'C.35G>A' in upper_name:
    return 'kras-g12d'
  if 'G12C' in upper_name or 'C.34G>T' in upper_name:
    return 'kras-g12c'
  return name.lower().replace(' ', '-').replace('.', '')

def get_pathway_id(name):
  if 'Homologous' in name:
    return 'hr-pathway'
  if 'EGFR' in name:
    return 'egfr-pathway'
  if 'RAS' in name:
    return 'mapk-pathway'
  return name.lower().replace(' ', '-')

def build_graph():
  """
  Loads raw databases and builds in-memory nodes and edges.
  """
  current = os.path.abspath(os.path.dirname(__file__))
  while current and not os.path.exists(os.path.join(current, 'datasets')):
    parent = os.path.dirname(current)
    if parent == current:
      break
    current = parent
  base_dir = current
  knowledge_dir = os.path.join(base_dir, 'datasets', 'knowledge')

  clinvar_path = os.path.join(knowledge_dir, 'clinvar.json')
  drugbank_path = os.path.join(knowledge_dir, 'drugbank.json')
  reactome_path = os.path.join(knowledge_dir, 'reactome.json')
  trials_path = os.path.join(knowledge_dir, 'clinical_trials.json')

  # Read files
  clinvar = []
  drugbank = []
  reactome = []
  clinical_trials = []

  if os.path.exists(clinvar_path):
    with open(clinvar_path, 'r', encoding='utf-8') as f:
      clinvar = json.load(f)
  if os.path.exists(drugbank_path):
    with open(drugbank_path, 'r', encoding='utf-8') as f:
      drugbank = json.load(f)
  if os.path.exists(reactome_path):
    with open(reactome_path, 'r', encoding='utf-8') as f:
      reactome = json.load(f)
  if os.path.exists(trials_path):
    with open(trials_path, 'r', encoding='utf-8') as f:
      clinical_trials = json.load(f)

  nodes = []
  edges = []

  # Add static patients
  patients_list = [
    {"id": "patient-a", "label": "Elena Rostova", "type": "Patient", "details": "Stage IIIC Ovarian Cancer"},
    {"id": "patient-b", "label": "Arthur Pendelton", "type": "Patient", "details": "Stage IV NSCLC"},
    {"id": "patient-c", "label": "Marcus Vance", "type": "Patient", "details": "Metastatic CRC"}
  ]
  nodes.extend(patients_list)

  # Add unique genes
  unique_genes = set()
  for p in reactome:
    for g in p.get('genes', []):
      if g not in unique_genes:
        unique_genes.add(g)
        nodes.append({"id": g, "label": g, "type": "Gene", "details": "Pathway gene"})
  if 'PARP1' not in unique_genes:
    nodes.append({"id": "PARP1", "label": "PARP1", "type": "Gene", "details": "Repair enzyme"})

  # Add mutations
  for m in clinvar:
    nodes.append({
      "id": get_mutation_id(m.get('variantName')),
      "label": m.get('variantName'),
      "type": "Mutation",
      "details": m.get('consequence')
    })

  # Add pathways
  for p in reactome:
    nodes.append({
      "id": get_pathway_id(p.get('name')),
      "label": p.get('name'),
      "type": "Pathway",
      "details": p.get('description')
    })

  # Add drugs
  for d in drugbank:
    nodes.append({
      "id": d.get('name').lower(),
      "label": d.get('name'),
      "type": "Drug",
      "details": d.get('mechanism')
    })
  nodes.append({
    "id": "erlotinib",
    "label": "Erlotinib",
    "type": "Drug",
    "details": "EGFR inhibitor"
  })

  # Add trials
  for t in clinical_trials:
    nodes.append({
      "id": t.get('trialId'),
      "label": t.get('trialId'),
      "type": "ClinicalTrial",
      "details": t.get('title')
    })

  # Toxicities
  nodes.extend([
    {"id": "neutropenia", "label": "Neutropenia", "type": "Toxicity", "details": "Myelosuppression"},
    {"id": "rash", "label": "Acneiform Rash", "type": "Toxicity", "details": "EGFR side effect"},
    {"id": "transaminitis", "label": "Transaminitis", "type": "Toxicity", "details": "Liver enzymes"}
  ])

  # Add patient edges
  edges.append({"source": "patient-a", "target": "brca1-mut", "type": "has_mutation"})
  edges.append({"source": "patient-b", "target": "egfr-l858r", "type": "has_mutation"})
  edges.append({"source": "patient-b", "target": "met-amp", "type": "has_mutation"})
  edges.append({"source": "patient-c", "target": "kras-g12d", "type": "has_mutation"})

  # Mutation to Gene
  for m in clinvar:
    edges.append({
      "source": get_mutation_id(m.get('variantName')),
      "target": m.get('geneSymbol'),
      "type": "associated_with"
    })

  # Gene to Pathway
  for p in reactome:
    path_id = get_pathway_id(p.get('name'))
    for g in p.get('genes', []):
      edges.append({"source": g, "target": path_id, "type": "associated_with"})

  # Drug targeting and toxicity
  for d in drugbank:
    drug_id = d.get('name').lower()
    for t in d.get('targets', []):
      edges.append({"source": drug_id, "target": t, "type": "inhibits"})

  edges.extend([
    {"source": "olaparib", "target": "brca1-mut", "type": "targets"},
    {"source": "osimertinib", "target": "egfr-l858r", "type": "targets"},
    {"source": "osimertinib", "target": "egfr-t790m", "type": "targets"},
    {"source": "savolitinib", "target": "met-amp", "type": "targets"},
    {"source": "amivantamab", "target": "met-amp", "type": "targets"},
    {"source": "mrtx1133", "target": "kras-g12d", "type": "targets"},
    {"source": "adagrasib", "target": "kras-g12c", "type": "targets"},
    {"source": "erlotinib", "target": "EGFR", "type": "inhibits"},
    {"source": "egfr-t790m", "target": "erlotinib", "type": "resistant_to"},

    {"source": "olaparib", "target": "neutropenia", "type": "causes"},
    {"source": "erlotinib", "target": "rash", "type": "causes"},
    {"source": "osimertinib", "target": "rash", "type": "causes"},
    {"source": "adagrasib", "target": "transaminitis", "type": "causes"},

    {"source": "NCT03737643", "target": "brca1-mut", "type": "enrolls"},
    {"source": "NCT03944772", "target": "met-amp", "type": "enrolls"},
    {"source": "NCT04077463", "target": "met-amp", "type": "enrolls"},
    {"source": "NCT04625881", "target": "kras-g12c", "type": "enrolls"}
  ])

  return nodes, edges

def find_causal_path(patient_id):
  nodes, edges = build_graph()
  
  # Find mutations
  active_mutations = [e['target'] for e in edges if e['source'] == patient_id and e['type'] == 'has_mutation']
  active_nodes = {patient_id}
  active_nodes.update(active_mutations)
  active_edges = []

  for mut_id in active_mutations:
    # Mutations -> Genes
    for e in edges:
      if e['source'] == mut_id and e['type'] == 'associated_with':
        active_nodes.add(e['target'])
        active_edges.append(e)
        
        # Genes -> Pathways
        for e2 in edges:
          if e2['source'] == e['target'] and e2['type'] == 'associated_with':
            active_nodes.add(e2['target'])
            active_edges.append(e2)

    # Target Drugs
    for e in edges:
      if e['target'] == mut_id and e['type'] == 'targets':
        active_nodes.add(e['source'])
        active_edges.append(e)

        # Drugs -> Toxicities
        for e2 in edges:
          if e2['source'] == e['source'] and e2['type'] == 'causes':
            active_nodes.add(e2['target'])
            active_edges.append(e2)

    # Trial Enrolls
    for e in edges:
      if e['target'] == mut_id and e['type'] == 'enrolls':
        active_nodes.add(e['source'])
        active_edges.append(e)

  # Resistance overlay
  for node_id in active_nodes:
    for e in edges:
      if e['source'] == node_id and e['type'] == 'resistant_to':
        if e['target'] in active_nodes:
          active_edges.append(e)

  # Filter out none/null
  node_map = {n['id']: n for n in nodes}
  sub_nodes = [node_map[id] for id in active_nodes if id in node_map]
  sub_edges = [e for e in active_edges if e['source'] in node_map and e['target'] in node_map]

  return sub_nodes, sub_edges
