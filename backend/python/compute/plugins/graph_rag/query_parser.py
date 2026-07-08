# Graph-RAG Query Parser and Entity Extractor
import re

def parse_query_entities(query_text):
  """
  Extracts targets and terms from patient queries.
  """
  upper = query_text.upper()
  
  drugs = []
  genes = []
  mutations = []
  diseases = []

  # Drug matches
  if "OLAPARIB" in upper or "LYNPARZA" in upper:
    drugs.append("olaparib")
  if "OSIMERTINIB" in upper or "TAGRISSO" in upper:
    drugs.append("osimertinib")
  if "ADAGRASIB" in upper or "KRAZATI" in upper:
    drugs.append("adagrasib")
  if "ERLOTINIB" in upper or "TARCEVA" in upper:
    drugs.append("erlotinib")

  # Gene matches
  if "BRCA1" in upper:
    genes.append("BRCA1")
  if "EGFR" in upper:
    genes.append("EGFR")
  if "KRAS" in upper:
    genes.append("KRAS")

  # Mutation matches
  if "C.1961DELA" in upper or "BRCA1-MUT" in upper or "DELA" in upper:
    mutations.append("brca1-mut")
  if "L858R" in upper:
    mutations.append("egfr-l858r")
  if "T790M" in upper:
    mutations.append("egfr-t790m")
  if "G12D" in upper:
    mutations.append("kras-g12d")

  # Disease matches
  if "OVARIAN" in upper or "CANCER" in upper:
    diseases.append("Ovarian Cancer")
  if "NSCLC" in upper or "LUNG" in upper:
    diseases.append("Lung Cancer")
  if "CRC" in upper or "COLORECTAL" in upper or "COLON" in upper:
    diseases.append("Colorectal Cancer")

  return {
    "drugs": list(set(drugs)),
    "genes": list(set(genes)),
    "mutations": list(set(mutations)),
    "diseases": list(set(diseases))
  }
