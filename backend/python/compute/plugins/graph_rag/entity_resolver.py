# Graph-RAG Entity Resolution Layer

SYNONYMS = {
  "tagrisso": "osimertinib",
  "lynparza": "olaparib",
  "krazati": "adagrasib",
  "tarceva": "erlotinib",
  "hrd": "BRCA1",
  "brca1-mut": "brca1-mut",
  "egfr-l858r": "egfr-l858r",
  "egfr-t790m": "egfr-t790m",
  "kras-g12d": "kras-g12d",
  # HGVSc notation resolver
  "c.1961dela": "brca1-mut",
  "c.2573t>g": "egfr-l858r",
  "c.2369c>t": "egfr-t790m",
  "c.35g>a": "kras-g12d"
}

def resolve_entity(term):
  """
  Resolves a synonym or trade term to its canonical counterpart.
  """
  clean = term.strip().lower()
  return SYNONYMS.get(clean, term)
