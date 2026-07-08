# PERSEPHONE SCR Literature Bibliography Vector Database Cache

LITERATURE_DATABASE = [
  {
    "pmid": "19447936",
    "title": "Adaptive Therapy",
    "journal": "Cancer Research",
    "year": 2009,
    "phase": "Preclinical/Theory",
    "abstract": "Adaptive therapy targets competitive interactions between drug-sensitive and drug-resistant tumor clones. By using treatment holidays, sensitive cells outcompete resistant clones, delaying tumor progression.",
    # High weight on Gatenby/Adaptive dimension
    "vector": [0.9, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]
  },
  {
    "pmid": "22960745",
    "title": "Systematic markers of drug sensitivity in cancer cells",
    "journal": "Nature",
    "year": 2012,
    "phase": "Preclinical Screen",
    "abstract": "Large-scale screening of cancer cell lines (CCLE/GDSC) identifies BRCA1 frameshift mutations as powerful markers of clinical sensitivity to PARP inhibitor Olaparib.",
    # High weight on Olaparib/BRCA1 dimension
    "vector": [0.1, 0.9, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]
  },
  {
    "pmid": "31542386",
    "title": "Osimertinib in Untreated EGFR-Mutated Advanced NSCLC",
    "journal": "New England Journal of Medicine",
    "year": 2018,
    "phase": "Phase III Trial",
    "abstract": "Osimertinib shows superior efficacy and profile over standard TKIs in patients with EGFR L858R and acquired T790M gatekeeper resistance mutations in non-small cell lung cancer.",
    # High weight on Osimertinib/EGFR dimension
    "vector": [0.1, 0.1, 0.9, 0.1, 0.1, 0.1, 0.1, 0.1]
  },
  {
    "pmid": "36458322",
    "title": "Adagrasib with or without Cetuximab in KRAS G12D CRC",
    "journal": "Journal of Clinical Oncology",
    "year": 2022,
    "phase": "Phase I/II Trial",
    "abstract": "Covalent inhibitor Adagrasib demonstrates high objective response rates in metastatic colorectal cancers harboring KRAS G12D somatic variants, particularly when combined with EGFR blockade.",
    # High weight on Adagrasib/KRAS dimension
    "vector": [0.1, 0.1, 0.1, 0.9, 0.1, 0.1, 0.1, 0.1]
  }
]

# Query text embeddings generator mapping keyword presence to search vectors
def embed_query_text(query_text):
  upper = query_text.upper()
  vec = [0.1] * 8
  
  if "ADAPTIVE" in upper or "HOLIDAY" in upper or "GATENBY" in upper:
    vec[0] = 0.95
  if "OLAPARIB" in upper or "BRCA1" in upper or "PARP" in upper:
    vec[1] = 0.95
  if "OSIMERTINIB" in upper or "EGFR" in upper or "T790M" in upper or "L858R" in upper:
    vec[2] = 0.95
  if "ADAGRASIB" in upper or "KRAS" in upper or "G12D" in upper:
    vec[3] = 0.95

  # Normalize vector
  mag = sum(x*x for x in vec) ** 0.5
  if mag > 0:
    vec = [x / mag for x in vec]
    
  return vec
