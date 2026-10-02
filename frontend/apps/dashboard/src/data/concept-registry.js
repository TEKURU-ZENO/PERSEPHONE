/**
 * PERSEPHONE Concept Registry
 * Ontology map standardizing synonyms and aliases to canonical biomedical concepts.
 */

export const conceptRegistry = {
  "brca1": {
    "type": "gene",
    "canonical": "BRCA1",
    "aliases": ["brca1", "brca1-mut", "hrd", "homologous recombination", "homologous recombination deficiency"]
  },
  "egfr": {
    "type": "gene",
    "canonical": "EGFR",
    "aliases": ["egfr", "egfr-l858r", "egfr-t790m", "t790m", "l858r", "kinase bypass"]
  },
  "kras": {
    "type": "gene",
    "canonical": "KRAS",
    "aliases": ["kras", "kras-g12d", "kras-g12c", "g12d", "g12c", "ras-mapk", "mapk"]
  },
  "met": {
    "type": "gene",
    "canonical": "MET",
    "aliases": ["met", "met-amp", "met amplification", "c-met"]
  },
  "olaparib": {
    "type": "drug",
    "canonical": "Olaparib",
    "aliases": ["olaparib", "lynparza", "parp", "parpi", "parp inhibitor"]
  },
  "osimertinib": {
    "type": "drug",
    "canonical": "Osimertinib",
    "aliases": ["osimertinib", "tagrisso", "egfr tki", "tki"]
  },
  "adagrasib": {
    "type": "drug",
    "canonical": "Adagrasib",
    "aliases": ["adagrasib", "krazati", "kras inhibitor", "kras g12c inhibitor", "g12c inhibitor"]
  },
  "savolitinib": {
    "type": "drug",
    "canonical": "Savolitinib",
    "aliases": ["savolitinib", "orpathys", "met inhibitor", "met tki"]
  },
  "amivantamab": {
    "type": "drug",
    "canonical": "Amivantamab",
    "aliases": ["amivantamab", "rybrevant", "egfr-met bispecific"]
  },
  "mrtx1133": {
    "type": "drug",
    "canonical": "MRTX1133",
    "aliases": ["mrtx1133", "kras g12d inhibitor (discontinued)", "g12d inhibitor"]
  },
  "adaptive": {
    "type": "strategy",
    "canonical": "ADAPTIVE",
    "aliases": ["adaptive", "adaptive dosing", "adaptive v1", "holiday", "treatment holiday"]
  },
  "mtd": {
    "type": "strategy",
    "canonical": "MTD",
    "aliases": ["mtd", "continuous mtd", "maximum tolerated dose", "continuous"]
  },
  "metronomic": {
    "type": "strategy",
    "canonical": "METRONOMIC",
    "aliases": ["metronomic", "low dose", "continuous low dose"]
  },
  "toxicity": {
    "type": "clinical",
    "canonical": "Toxicity",
    "aliases": ["toxicity", "side effect", "adverse event", "warnings", "violation"]
  }
};
