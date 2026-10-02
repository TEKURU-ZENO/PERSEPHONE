# COSMIC Mutational Signatures Reference Data

This directory contains official reference datasets for cancer mutational signature analysis and deconvolution in the PERSEPHONE platform.

## Datasets

### 1. `cosmic_sbs96_reference.csv`
- **Version**: COSMIC Mutational Signatures Version 3.4 (Released October 2023)
- **Reference Genome**: GRCh37 / hg19
- **Channels**: 96 standard trinucleotide single-base substitution contexts:
  - 6 substitution classes: $C>A, C>G, C>T, T>A, T>C, T>G$
  - 16 flanking 5' and 3' base permutations per class (96 channels total)
- **Signatures**: 86 curated mutational signatures (`SBS1` through `SBS99`)
- **Source**: Catalogue Of Somatic Mutations In Cancer (COSMIC) / Wellcome Sanger Institute via Alexandrov Lab (`SigProfilerAssignment/data/Reference_Signatures/GRCh37/COSMIC_v3.4_SBS_GRCh37.txt`)
- **Format**: CSV matrix with 96 rows and 87 columns (Context `Type` + 86 signature profiles)
- **SHA-256 Checksum**:
  ```
  f9150fe1f39ee695c215d171255c1d8ab893634c03e7e8f16b3e73cdedc91de4
  ```

## Biological Validation Baselines
- **SBS1** (Spontaneous 5-methylcytosine deamination with aging): Signature profile peaks specifically at `NpCpG` trinucleotide contexts (`A[C>T]G`, `C[C>T]G`, `G[C>T]G`, `T[C>T]G`).
- **SBS7a** (Ultraviolet light damage): Signature profile peaks specifically at dipyrimidine contexts (`C[C>T]N`, `T[C>T]N`).
- **SBS3** (Homologous Recombination Deficiency / BRCA1/2 disruption): Broad mutation distribution across all 96 contexts.
- **SBS6** / **SBS15** / **SBS20** / **SBS26** (Mismatch Repair Deficiency): Dense C>T transitions and small indels.
