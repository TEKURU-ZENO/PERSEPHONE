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
  },
  {
    "mutationId": "VCV000000000",
    "geneSymbol": "MET",
    "variantName": "MET Amplification",
    "classification": "Pathogenic",
    "consequence": "Gene amplification mediating bypass resistance to EGFR TKIs",
    "vaf": "N/A",
    "hgvsc": "Copy Gain",
    "timestamp": "2026-06-29T16:40:34.609Z"
  },
  {
    "mutationId": "VCV000012582",
    "geneSymbol": "KRAS",
    "variantName": "KRAS G12C",
    "classification": "Pathogenic",
    "consequence": "Cysteine substitution in codon 12 sensitive to covalent inhibitors",
    "vaf": "N/A",
    "hgvsc": "c.34G>T",
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
    "mechanism": "Highly selective, covalent small-molecule inhibitor of KRAS G12C mutation, blocking GTPase signaling cascades.",
    "targets": [
      "KRAS"
    ],
    "brandNames": [
      "Krazati"
    ],
    "halfLife": "23 hours",
    "timestamp": "2026-06-29T16:40:34.610Z"
  },
  {
    "drugId": "savolitinib",
    "name": "Savolitinib",
    "mechanism": "Potent and selective oral MET tyrosine kinase inhibitor targeting MET amplification.",
    "targets": [
      "MET"
    ],
    "brandNames": [
      "Orpathys"
    ],
    "halfLife": "5 hours",
    "timestamp": "2026-06-29T16:40:34.610Z"
  },
  {
    "drugId": "amivantamab",
    "name": "Amivantamab",
    "mechanism": "Bispecific antibody directed against EGFR and MET extracellular domains to overcome resistance.",
    "targets": [
      "EGFR",
      "MET"
    ],
    "brandNames": [
      "Rybrevant"
    ],
    "halfLife": "11 days",
    "timestamp": "2026-06-29T16:40:34.610Z"
  },
  {
    "drugId": "mrtx1133",
    "name": "MRTX1133",
    "mechanism": "Non-covalent, selective small-molecule inhibitor of KRAS G12D (discontinued 2025).",
    "targets": [
      "KRAS"
    ],
    "brandNames": [],
    "halfLife": "N/A",
    "status": "discontinued (2025)",
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
      "GAB1",
      "MET"
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
    "trialId": "NCT03737643",
    "title": "Durvalumab + Bevacizumab + Olaparib in Advanced Ovarian Cancer (DUO-O)",
    "phase": "Phase III",
    "status": "Active, not recruiting",
    "conditions": [
      "Ovarian Cancer",
      "Fallopian Tube Cancer",
      "Peritoneal Cancer"
    ],
    "enrollmentCriteria": "Newly diagnosed advanced ovarian cancer with confirmed BRCA1/2 alteration or HRD positive.",
    "timestamp": "2026-06-29T16:40:34.610Z"
  },
  {
    "trialId": "NCT03944772",
    "title": "Phase Ib/II Trial of Osimertinib + Savolitinib in Patients with EGFRm-positive and MET-amplified NSCLC (ORCHARD)",
    "phase": "Phase II",
    "status": "Active, not recruiting",
    "conditions": [
      "Non-Small Cell Lung Cancer (NSCLC)"
    ],
    "enrollmentCriteria": "Histologically confirmed NSCLC harboring EGFR activating mutation (L858R or Exon 19 del) with acquired MET amplification following disease progression on first-line osimertinib.",
    "timestamp": "2026-06-29T16:40:34.610Z"
  },
  {
    "trialId": "NCT04077463",
    "title": "Phase Ib/II Study of Amivantamab and Lazertinib in EGFR-Mutated NSCLC Post-Osimertinib (CHRYSALIS-2)",
    "phase": "Phase Ib/II",
    "status": "Active, not recruiting",
    "conditions": [
      "Non-Small Cell Lung Cancer (NSCLC)"
    ],
    "enrollmentCriteria": "EGFR-mutated advanced NSCLC with disease progression on prior osimertinib; targets EGFR and MET bypass. Published Cohort A requires prior platinum.",
    "timestamp": "2026-06-29T16:40:34.610Z"
  },
  {
    "trialId": "NCT03785249",
    "title": "Phase 1/2 Study of MRTX849 (Adagrasib) in Patients with Advanced Solid Tumors with KRAS G12C Mutation (KRYSTAL-1)",
    "phase": "Phase I/II",
    "status": "Active, not recruiting",
    "conditions": [
      "Colorectal Cancer",
      "Advanced Solid Tumors"
    ],
    "enrollmentCriteria": "Histologically confirmed metastatic colorectal adenocarcinoma or solid tumor with confirmed KRAS G12C mutation (not G12D).",
    "timestamp": "2026-06-29T16:40:34.610Z"
  }
];

export { verifiedTrials } from './verified-trials.js';
