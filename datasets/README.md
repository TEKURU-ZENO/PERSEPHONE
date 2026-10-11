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

3. **Real Clinical Benchmark: Bruchovsky 2006 / Tanaka 2010 Intermittent Androgen Suppression (IAS):**
   - **Sources:**
     - Bruchovsky et al., *Cancer* 2006; 107(2):389–395.
     - Tanaka et al., *Phil. Trans. R. Soc. A* 2010; 368:5029–5044.
   - **Public Archive:** `http://www.nicholasbruchovsky.com/dataTanaka.zip`
   - **Canonical SHA-256 Checksum:** `845683954e99253ddf68e488a48223e89c19247a92aec27daa79130d8f46904f` (91,538 bytes).
   - **Automated Fetch Script:** `scripts/fetch_ias_data.py` (extracts to `data/ias_bruchovsky/`).
   - **Cohort Breakdown:** 90 total longitudinal patient trajectories across 2 cohorts:
     - `Bruchovsky_et_al`: 72 patients from the Vancouver IAS trial.
     - `Shaw_et_al`: 18 patients.
     - 88/90 patients have $\ge 2$ complete treatment cycles.
   - **Clinical Protocol & Cycling Rules:**
     - *On-Treatment Phase (Phase 1 / status 1):* Combined androgen blockade with cyproterone acetate (CPA, 100–200 mg/day oral) and leuprolide acetate (7.5 mg depot injection). Administered until serum PSA decreased to normal/nadir (<4 ng/mL or undetectable) for $\ge 2$ consecutive visits.
     - *Off-Treatment Phase (Phase 2 / status 0):* Androgen deprivation discontinued. PSA closely monitored until elevation exceeded clinical threshold (>10 ng/mL or clinical symptoms), triggering the subsequent on-treatment cycle.
   - **Dataset Schema (10 comma-separated columns):**
     | Column Index | Field Name | Unit / Type | Description |
     | :--- | :--- | :--- | :--- |
     | 0 | `patient_id` | Integer / String | Unique patient identifier |
     | 1 | `date` | YYYY/M/D HH:MM:SS | Calendar timestamp of assessment |
     | 2 | `cpa_dose` | mg/day | Cyproterone acetate dose (0, 100, 200) |
     | 3 | `leuprolide_dose` | mg | Leuprolide acetate depot injection dose (7.5) |
     | 4 | `psa` | ng/mL | Serum Prostate Specific Antigen |
     | 5 | `testosterone` | nmol/L | Serum testosterone level |
     | 6 | `cycle` | Integer ($\ge 1$) | Treatment cycle sequence number |
     | 7 | `treatment_status` | Binary (1/0) | $1 = \text{on-treatment}$, $0 = \text{off-treatment}$ |
     | 8 | `julian_days` | Days | Julian calendar day index |
     | 9 | `elapsed_days` | Days | Elapsed days from cycle 1 baseline |
   - **Cancer Type Scope & Simulation Disclosure:**
     - Prostate cancer IAS is the canonical benchmark in mathematical oncology for competitive Lotka-Volterra adaptive therapy models.
     - All validation and parameter identifiability benchmarks in Phase 3 are executed on this authentic human clinical data.
     - Demonstration patients for ovarian, lung, and colorectal cancer in PERSEPHONE remain synthetic/simulated and are explicitly labeled as such across the UI and API.

