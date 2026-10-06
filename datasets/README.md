# Multi-Omics Datasets & Clinical Knowledge Bases

This directory houses the structured genomic, clinical trial, and biological reference datasets used by PERSEPHONE.

---

## Catalog Structure

```
datasets/
├── reference/
│   └── cosmic_sbs96_reference.csv       # Authentic COSMIC v3.4 SBS 96x86 mutational signatures
├── knowledge/
│   ├── verified_trials.json             # 16 authentic ClinicalTrials.gov verified protocols
│   ├── clinical_trials.json             # Structured trial eligibility schemas and criteria
│   ├── clinvar.json                     # Curated variant pathogenicity references
│   ├── drugbank.json                    # Drug mechanisms, targets, and metabolic pathways
│   └── reactome.json                    # Canonical biological signaling pathways
├── features/
│   ├── tcga_ovarian_cohort.json         # TCGA High-Grade Serous Ovarian cohort samples
│   └── ccle_reference_lines.json        # Cancer Cell Line Encyclopedia reference lines
├── raw/                                 # Raw clinical & pharmacogenomic data extracts (GDSC, CCLE, TCGA)
└── reports/data-quality/                # ETL data quality and completeness QC reports
```

---

## Data Verification & Fidelity

1. **COSMIC v3.4 SBS96 Reference Matrix:**
   - Curated 96 substitution contexts across 86 signatures.
   - Canonical LF SHA-256 hash: `aad0be68be61cb94674d8c5c01309f7ab9670cfcd610966d00b3f0883feeec72`.
   - Verified by automated test suite (`test_drug_target_consistency.py`).

2. **Verified Clinical Trials Knowledge Base:**
   - Contains 16 verified NCT records checked against ClinicalTrials.gov (October 2026).
   - Zero fallback or synthetic trial IDs allowed in compute pipelines.
   - 100% key and content parity enforced with frontend registry (`verified-trials.js`).
