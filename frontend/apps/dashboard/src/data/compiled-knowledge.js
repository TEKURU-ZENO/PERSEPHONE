/**
 * PERSEPHONE Compiled Knowledge Database
 * Generated automatically by the ingestion pipeline on 2026-06-29T16:40:34.611Z.
 * Grounded in ClinVar, DrugBank, Reactome, and ClinicalTrials.gov data feeds.
 */

export const clinvar = [
  {
    "mutationId": "VCV000055474",
    "geneSymbol": "BRCA1",
    "variantName": "BRCA1 c.1961delA",
    "classification": "Pathogenic",
    "consequence": "Frameshift leading to Homologous Recombination Deficiency (HRD)",
    "vaf": "N/A",
    "hgvsc": "c.1961delA",
    "timestamp": "2026-06-29T16:40:34.608Z"
  },
  {
    "mutationId": "VCV000016618",
    "geneSymbol": "EGFR",
    "variantName": "EGFR L858R",
    "classification": "Pathogenic",
    "consequence": "Constitutive kinase domain activation",
    "vaf": "N/A",
    "hgvsc": "c.2573T>G",
    "timestamp": "2026-06-29T16:40:34.609Z"
  },
  {
    "mutationId": "VCV000016620",
    "geneSymbol": "EGFR",
    "variantName": "EGFR T790M",
    "classification": "Pathogenic",
    "consequence": "Acquired gatekeeper TKI resistance mutation",
    "vaf": "N/A",
    "hgvsc": "c.2369C>T",
    "timestamp": "2026-06-29T16:40:34.609Z"
  },
  {
    "mutationId": "VCV000012574",
    "geneSymbol": "KRAS",
    "variantName": "KRAS G12D",
    "classification": "Pathogenic",
    "consequence": "Hotspot mutation trapping GTP-bound active state",
    "vaf": "N/A",
    "hgvsc": "c.35G>A",
    "timestamp": "2026-06-29T16:40:34.609Z"
  }
];
export const drugbank = [
  {
    "drugId": "olaparib",
    "name": "Olaparib",
    "mechanism": "PARP1 and PARP2 selective inhibitor, exploiting synthetic lethality under BRCA1/2 repair deficiencies.",
    "targets": [
      "PARP1",
      "PARP2"
    ],
    "brandNames": [
      "Lynparza"
    ],
    "halfLife": "11.9 hours",
    "timestamp": "2026-06-29T16:40:34.610Z"
  },
  {
    "drugId": "osimertinib",
    "name": "Osimertinib",
    "mechanism": "Third-generation, irreversible tyrosine kinase inhibitor targeting EGFR activating (L858R) and gatekeeper resistance (T790M) mutations.",
    "targets": [
      "EGFR"
    ],
    "brandNames": [
      "Tagrisso"
    ],
    "halfLife": "48 hours",
    "timestamp": "2026-06-29T16:40:34.610Z"
  },
  {
    "drugId": "adagrasib",
    "name": "Adagrasib",
    "mechanism": "Highly selective, covalent small-molecule inhibitor of KRAS G12D mutation, blocking GTPase signaling cascades.",
    "targets": [
      "KRAS"
    ],
    "brandNames": [
      "Krazati"
    ],
    "halfLife": "23 hours",
    "timestamp": "2026-06-29T16:40:34.610Z"
  }
];
export const reactome = [
  {
    "pathwayId": "R-HSA-5685939",
    "name": "Homologous Recombination",
    "description": "Double-strand DNA repair pathway critical for genome integrity.",
    "genes": [
      "BRCA1",
      "BRCA2",
      "RAD51",
      "PALB2"
    ]
  },
  {
    "pathwayId": "R-HSA-177929",
    "name": "EGFR Kinase Signaling",
    "description": "Tyrosine kinase phosphorylation cascade driving cell survival and proliferation.",
    "genes": [
      "EGFR",
      "GRB2",
      "SOS1",
      "GAB1"
    ]
  },
  {
    "pathwayId": "R-HSA-5673001",
    "name": "RAS-MAPK Cascade",
    "description": "Mitogen-activated protein kinase signaling loop transferring extracellular growth cues.",
    "genes": [
      "KRAS",
      "HRAS",
      "NRAS",
      "BRAF",
      "RAF1",
      "MAP2K1",
      "MAPK1"
    ]
  }
];
export const clinicalTrials = [
  {
    "trialId": "NCT04381884",
    "title": "Phase II Study of Olaparib Combinations in HRD-Positive Advanced Ovarian Cancer",
    "phase": "Phase II",
    "status": "Active, Recruiting",
    "conditions": [
      "Ovarian Cancer",
      "Fallopian Tube Cancer",
      "Peritoneal Cancer"
    ],
    "enrollmentCriteria": "Confirmed pathogenic somatic mutation in BRCA1 or BRCA2; homologous recombination deficiency positive.",
    "timestamp": "2026-06-29T16:40:34.610Z"
  },
  {
    "trialId": "NCT03944772",
    "title": "Phase III Trial of Osimertinib Combination Therapies in Patients with EGFRm-positive and MET-amplified NSCLC",
    "phase": "Phase III",
    "status": "Active, Recruiting",
    "conditions": [
      "Non-Small Cell Lung Cancer (NSCLC)"
    ],
    "enrollmentCriteria": "EGFR mutated (L858R or Exon 19 del) with acquired T790M gatekeeper mutation.",
    "timestamp": "2026-06-29T16:40:34.610Z"
  },
  {
    "trialId": "NCT04625881",
    "title": "Study of KRAS Inhibitor Combinations in Advanced Gastrointestinal and Colorectal Malignancies",
    "phase": "Phase I/II",
    "status": "Active, Recruiting",
    "conditions": [
      "Colorectal Cancer",
      "Pancreatic Cancer"
    ],
    "enrollmentCriteria": "Histologically confirmed metastatic colorectal adenocarcinoma with KRAS G12D mutation.",
    "timestamp": "2026-06-29T16:40:34.610Z"
  }
];
