# PERSEPHONE Workstation Walkthrough & Demo Script

This script provides reviewers, clinicians, and researchers with a step-by-step narrative to explore the key clinical features of the PERSEPHONE workstation across all 20 implemented phases.

---

## Part 1: Baseline Profiles & Foundational Engines

### Demo 1: Patient A (BRCA1-Mutant Ovarian Cancer)
- **Objective:** Demonstrate synthetic lethality and clonal selection modeling.
- **Narrative Steps:**
  1. In the top header panel, select **Elena Rostova** (Patient A).
  2. Observe her profile in the left panel: Stage IIIC High-Grade Serous Ovarian Cancer (`Stage IIIC HGSOC`), somatic pathogenic `BRCA1 c.1961delA` (VAF 42.3%), and baseline CA-125 kinetics.
  3. Inspect real-time telemetry fluctuations driven by the stochastic Brownian motion IoT stream.
  4. View the associated histopathology slide rendered via the secure server proxy.

### Demo 2: Patient B (EGFR-Mutant NSCLC with Acquired Resistance)
- **Objective:** Analyze bypass pathway activation and drug resistance selection.
- **Narrative Steps:**
  1. Select **Arthur Pendelton** (Patient B).
  2. Review genomics: Activating `EGFR L858R` (VAF 48.9%) with secondary `MET amplification` (CN=12) driving third-generation TKI resistance.
  3. Arthur is marked as `Progressive Disease` post-osimertinib due to MET bypass pathway activation.

### Demo 3: Patient C (KRAS G12D Colorectal Cancer & Negative Screening)
- **Objective:** Validate strict biomarker filtering and contraindication management.
- **Narrative Steps:**
  1. Select **Marcus Vance** (Patient C).
  2. Review profile: Stage IV Colorectal Adenocarcinoma, `KRAS G12D` (`p.Gly12Asp`), Microsatellite Stable (`MSS`), and baseline transaminitis (Grade 2 liver toxicity).
  3. Note that Marcus possesses `KRAS G12D`, which is completely distinct from `KRAS G12C`.

### Demo 4: RK4 Simulator & Regimen Scenario Simulator (Tab 2)
- **Objective:** Compare forward ODE projections under alternative dosing regimens (MTD vs. Adaptive).
- **Narrative Steps:**
  1. Open the **Simulation Lab** panel (Tab 2).
  2. Select **Arthur Pendelton** (Patient B) and the **MTD** strategy. Observe the numerical simulation curve: continuous therapy delivers cumulative dose 260.0 with peak toxicity 12.26; tumor volume remains controlled below the 120% progression threshold within the 180-day window (TTP: 180 days).
  3. Switch comparison slider to **Adaptive**. Dosing halts when tumor volume drops below 50% ($0.5 \times V_0$) and resumes when rebounding above 100% ($V_0$).
  4. For Patient B, adaptive dosing maintains tumor control without progression within 180 days (TTP: 180 days) while reducing cumulative dose from 260.0 to 100.0 (a 61.5% reduction) with lower peak toxicity (11.31 vs 12.26).
  *(Command: `python -c "from backend.python.compute.simulation.core.simulator import simulate_trajectory; from backend.python.compute.common.models.patient import PatientTwin; p=PatientTwin('patient-b', 'Arthur', 'Stage IV', 'NSCLC'); m=simulate_trajectory(p, 'mtd', {}); a=simulate_trajectory(p, 'adaptive', {}); print(f'MTD: TTP={m.time_to_progression}d, CumDose={m.cumulative_dose}, MaxTox={m.max_toxicity}; Adaptive: TTP={a.time_to_progression}d, CumDose={a.cumulative_dose}, MaxTox={a.max_toxicity}')"`)*
  *(Note on parameter sensitivity: In Elena Rostova / Patient A, holding dose during regression permits sensitive cell rebound reaching progression threshold at day 77 [TTP = 77 days vs 180 days for MTD], demonstrating that without patient-specific parameter calibration, the uncalibrated model does not confer an adaptive survival advantage across all patient baselines).*

### Demo 5: 2D Canvas Knowledge Graph Explorer (Tab 3)
- **Objective:** Trace causal biological pathways interactively.
- **Narrative Steps:**
  1. Navigate to **Knowledge Graph Explorer** (Tab 3).
  2. Hover over Arthur Pendelton to highlight the causal bypass route:
     `Arthur Pendelton` $\to$ `MET amp` $\to$ `MET` $\to$ `met-pathway` $\to$ `savolitinib` $\to$ `NCT03944772` (SAVANNAH Trial).
  3. Verify that zero fabricated drug target edges exist in the network.

---

## Part 2: Multimodal & Genomic Intelligence

### Demo 6: Multimodal Diagnostic Lab (Tab 11)
- **Objective:** Explore quantitative pathology and volumetric radiology.
- **Narrative Steps:**
  1. Switch to **Multimodal Lab** (Tab 11).
  2. Under the **Pathology** sub-tab, click **Run Pipeline** to tile the slide and compute tumor purity, necrosis, and cellularity scorecards.
  3. Switch to **Radiology**, select CT or MRI, and execute volumetric segmentation to view cross-sectional slice masks and radiomics texture features.
  4. Notice the honest `— (Simulated)` label displaying on model confidence gauges.

### Demo 7: Genomic Intelligence & COSMIC Mutational Signatures (Tab 12)
- **Objective:** Deconvolve mutational etiology using Non-Negative Least Squares (NNLS).
- **Narrative Steps:**
  1. Switch to **Genomic Intelligence** (Tab 12).
  2. Select Elena Rostova and click **Deconvolve Signatures**.
  3. The NNLS solver fits the 96-trinucleotide substitution spectrum against the authentic COSMIC v3.4 SBS matrix:
     - Elena shows dominant **SBS3** exposure (Homologous Recombination Deficiency / BRCA1/2).
     - Marcus Vance shows clock-like **SBS1** (spontaneous 5-methylcytosine deamination) and **SBS5**.

### Demo 8: Clinical Trials Intelligence & Negative Screening (Tab 13)
- **Objective:** Demonstrate precision biomarker matching and exclusion guarantees.
- **Narrative Steps:**
  1. Open **Clinical Trials** (Tab 13).
  2. Select **Patient B** (EGFR + MET): Matches active NSCLC combination trials (CHRYSALIS-2 `NCT04077463`, MARIPOSA-2 `NCT04988295`, ORCHARD `NCT03944772`). Closed trials are accurately labeled `"biomarker match, not enrolling"`.
  3. Select **Patient C** (KRAS G12D Colorectal):
     - The matcher rejects KRYSTAL-1 (`NCT03785249`) strictly due to mutation mismatch (*"Trial requires KRAS G12C, patient has KRAS G12D"*).
     - The matcher rejects KEYNOTE-177 (`NCT02563002`) due to microsatellite mismatch (*"Trial requires MSI-H, patient has MSS"*).
     - Renders an explicit clinical screening note: *"No currently recruiting trials match Patient C's biomarker profile"*, and `topTrial` safely defaults to `None`.

---

## Part 3: Advanced Council, Research & OS Governance

### Demo 9: Longitudinal Monitoring & Molecular Lead-Time (Tab 14)
- **Objective:** Detect preclinical relapse prior to radiographic RECIST progression.
- **Narrative Steps:**
  1. Navigate to **Clinical Monitoring** (Tab 14).
  2. Inspect the time-series plot comparing radiographic sum of longest diameters (RECIST 1.1) with circulating tumor DNA (`ctDNA VAF`).
  3. Observe the molecular lead-time alert: ctDNA rebound precedes radiographic progression by 65 days (day 300 molecular relapse vs day 365 radiographic progression; timeline lead time: 60-65 days), triggering early regimen re-evaluation.
  *(Command: `python -c "from backend.python.compute.monitoring.timeline import PatientTimeline; tl=PatientTimeline.get_patient_timeline('patient-a'); print([(e['day'], e['title']) for e in tl if 'Progress' in e['title'] or 'Recurrence' in e['title']])"`)*

### Demo 10: Counterfactual Research Lab (Tab 16)
- **Objective:** Conduct in-silico multi-arm trial simulation across synthetic cohorts.
- **Narrative Steps:**
  1. Switch to **Counterfactual Lab** (Tab 16).
  2. Click **Generate Synthetic Cohort** (100 in-silico patients stratified by biomarker).
  3. Run parallel RK4 simulations across Arm A (Continuous MTD) and Arm B (Adaptive Dosing).
  4. Inspect the Kaplan-Meier progression-free survival estimates and review the formal Potential Outcomes Causal Assumption Manifest ($Y(a) = f(X, a, U_Y)$).

### Demo 11: Research Intelligence & Cryptographic Citation Lineage (Tab 17)
- **Objective:** Inspect guideline conformance, contradiction detection, and cryptographic provenance.
- **Narrative Steps:**
  1. Switch to **Research Intelligence** (Tab 17).
  2. Review automated NCCN, ASCO, and ESMO guideline extraction.
  3. Observe contradiction detection highlighting conflicting first-line recommendations.
  4. Inspect the SHA-256 hash chain provenance root hash verifying cryptographic citation integrity.

### Demo 12: Clinical Governance & PERSEPHONE OS Cockpit (Tabs 18 & 19)
- **Objective:** Trigger deterministic safety gates and audit bit-level case replay.
- **Narrative Steps:**
  1. Switch to **Clinical Governance** (Tab 18).
  2. Inspect the deterministic KDIGO 2024, CTCAE v5.0, and CPIC rule engines.
  3. Observe how severe organ contraindications or high multimodal discordance trigger the **Clinical Abstention Engine** with transparent reason codes.
  4. Switch to **PERSEPHONE OS** (Tab 19).
  5. Inspect the 5-plane telemetry board, view the live `BlackboardMemory` state, and click **Replay Experiment** to verify bit-level ODE and decision reproduction (RMSE $< 1\times 10^{-4}$) against the SHA-256 sealed `ExperimentManifest`.
