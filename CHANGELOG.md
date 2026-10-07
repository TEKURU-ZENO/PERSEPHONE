# Changelog

All notable changes to the PERSEPHONE platform across its 20 development phases are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2026-10-06 // PERSEPHONE OS Capstone Release

### Added
- **Phase 20 — PERSEPHONE OS Capstone Layer:**
  - Unified 23-Agent Council orchestrated across 5 Intelligence Planes (Patient, Scientific, Clinical, Evidence, Governance).
  - Implemented `PersephoneKernel` DAG scheduler with 3-tier failure containment.
  - Implemented thread-safe `BlackboardMemory`, non-blocking `OSEventBus`, and SHA-256 hash chain `ProvenanceLedger`.
  - Added `ExperimentManifest` (Schema v1.0, SHA-256 seal) and `CaseReplayEngine` with bit-level reproducibility (RMSE $< 1\times 10^{-4}$).
  - Mounted Tab 19 PERSEPHONE OS Cockpit with live telemetry and state replay.
- **Phase 19 — Clinical Safety, Governance & Validation Platform:**
  - Implemented deterministic rule engines for KDIGO 2024 (renal staging), CTCAE v5.0 (toxicity grading), and CPIC guidelines.
  - Deployed Clinical Abstention Engine with 4 strict reason codes (`REASON_SEVERE_CONTRAINDICATION`, `REASON_EVIDENCE_CONTRADICTION`, `REASON_MULTIMODAL_DISCORDANCE`, `REASON_EXCESSIVE_UNCERTAINTY`).
  - Added Multimodal Discordance Index and Expected Calibration Error (ECE / Brier score) metrics.
  - Added Tab 18 Clinical Governance panel.
- **Phase 18 — Clinical Knowledge & Research Intelligence Platform:**
  - Added 22nd Council Agent (`ResearchIntelligenceAgent`).
  - Automated guideline parsing for NCCN, ASCO, and ESMO clinical recommendations.
  - Implemented temporal validity tracking, guideline contradiction detection, and cryptographic SHA-256 hash chain citation lineage.
  - Enforced clinical Grounding Gate rejecting ungrounded recommendations.
  - Added Tab 17 Research Intelligence panel.
- **Phase 17 — Synthetic Cohort & Counterfactual Research Platform:**
  - Added 21st Council Agent (`CounterfactualResearchAgent`).
  - Implemented in-silico multi-arm clinical trial simulator across parameterized synthetic cohorts.
  - Deployed Potential Outcomes Causal Assumption Manifest ($Y(a) = f(X, a, U_Y)$).
  - Added Tab 16 Counterfactual Lab.

### Changed
- Replaced PPO reinforcement learning algorithm with continuous/discretized Actor-Critic network and policy (`actor_critic.py`, `actor_critic_policy.py`), purging all PPO aliases.
- Corrected Clinical Trials matcher: implemented standard 3-to-1 protein change normalization (`p.Gly12Asp` $\to$ `G12D`), organ/cancer lineage checking, and negative mutation screening for Patient C.
- Honest labeling: flagged all 8 simulated imaging and feature modules with `is_mock: True` and replaced simulated confidence scores with `— (Simulated)`.
- Replaced all local `file:///` URIs across documentation with repository-relative links.

---

## [1.5.0] - 2026-09-15 // Multimodal Diagnostics & Longitudinal Intelligence

### Added
- **Phase 16 — Response Intelligence & Digital Biomarkers Platform:**
  - Multimodal response classifier, RECIST response kinetic modeler, resistance escape prediction, and composite digital biomarker synthesis.
  - Added Tab 15 Response Intelligence panel.
- **Phase 15 — Clinical Monitoring & Longitudinal Intelligence Platform:**
  - Longitudinal time-series biomarker tracking and RECIST 1.1 radiographic tumor burden kinetics.
  - Molecular lead-time detection identifying ctDNA rebound prior to radiographic progression.
  - Added Tab 14 Clinical Monitoring panel.
- **Phase 14 — Clinical Trials Intelligence Platform:**
  - Verified ClinicalTrials.gov registry integration (16 authentic trials).
  - Biomarker and cancer lineage matching with status labeling (`biomarker match, not enrolling`).
  - Added Tab 13 Clinical Trials panel.
- **Phase 13 — Genomic Intelligence & Pharmacogenomics Platform:**
  - Somatic variant annotator and Non-Negative Least Squares (NNLS) deconvolution against authentic COSMIC v3.4 SBS 96x86 reference matrix.
  - Drug-gene interaction resolver and combination synergy predictor.
  - Added Tab 12 Genomic Intelligence panel.
- **Phase 12 — Multimodal Imaging Intelligence Platform:**
  - Whole Slide Image (WSI) loader, grid tiler, and tumor purity/necrosis estimators.
  - Volumetric CT/MRI segmentation and radiomics shape/texture feature extractors.
  - GradCAM heatmaps and multi-head attention map rollouts (flagged `is_mock: True`).
  - Added Tab 11 Multimodal Lab panel.

---

## [1.2.0] - 2026-08-01 // Reasoning Engines & Reinforcement Learning

### Added
- **Phase 11 — Clinical AI Runtime (CAIR) & Council Foundations:**
  - Execution context scoping, provider middleware, health check daemons, and initial 14-agent council coordination.
  - Added Tab 10 Clinical AI Runtime panel.
- **Phase 10 — Clinical Model Calibration & Uncertainty Quantification:**
  - Model calibration against clinical benchmark parameter ranges and parametric bootstrap confidence intervals.
  - Added Tab 9 Clinical Validation panel.
- **Phase 9 — Reinforcement Learning Dosing Policy Optimization:**
  - Gymnasium-compatible environment (`OncologyGymEnv`), Deep Q-Network (DQN) trainer, and treatment holiday scheduling.
  - Added Tab 8 Policy Optimization panel.
- **Phase 8 — Graph-RAG v2 Hybrid Reasoning Engine:**
  - Entity resolution, vector search, multi-hop graph expansion, and clinical grounding gates.
  - Added Tab 7 Evidence Graph-RAG panel.
- **Phase 7 — Scientific Compute Runtime (SCR) & Parity Engine:**
  - Python microservice (Port 5000) coupled with Node gateway (Port 3000).
  - Cross-language RK4 simulation parity (RMSE $< 1\times 10^{-4}$) and graph pathfinding parity.
- **Phase 6 — Multi-Omics Dataset Ingestion & Feature Store:**
  - Canonical schemas and ETL quality control pipelines for TCGA, CCLE, GDSC, ClinVar, DrugBank, and Reactome.
  - Added Tab 6 Patient Simulation Profile Biobank panel.
- **Phase 5 — Clinical Memory Workspace & Graph-Linking:**
  - TF-IDF concept parsing, relevance scoring, memory retrieval, REST persistence, and visual graph node dispatching.
  - Added Tab 5 Clinical Memory Workspace panel.

---

## [1.0.0] - 2026-06-05 // Foundation Workstation

### Added
- **Phase 1 — Simulation Profile Operating Environment (DTOE):**
  - Palantir-style header metrics and responsive workstation grids.
  - Decoupled patient record system (`patients.js`) and observable state controller (`patient.store.js`).
  - Integrated IoT biometric simulator with stochastic walks.
  - High-resolution tissue slide and scanning overlay.
- **Phase 2 — Tumor Dynamics Simulation Engine:**
  - Fourth-Order Runge-Kutta (RK4) numerical ODE solver.
  - Coupled Lotka-Volterra competition dynamics ($S_S$ vs $S_R$) with resistance fitness cost ($\alpha_2 < \alpha_1$).
  - Single-compartment PK and systemic toxicity PD accumulation models.
  - Rule-based Adaptive Therapy logic (hold at 50%, resume at 100%).
  - Regimen Scenario Simulator comparing prospective alternative dosing projections.
- **Phase 3 — Biomedical Knowledge Graph Explorer:**
  - Literature-linked Parameter Registry database (`parameter-registry.json`).
  - Interactive zero-dependency canvas force-directed 2D Knowledge Graph explorer mapping mutations to clinical trials.
- **Phase 4 — Evidence-Grounded Tumor Board (Deterministic DAG):**
  - Stateful 5-agent DAG orchestrator execution service (`Evolution` $\to$ `Planning` $\to$ `Evidence` $\to$ `Safety` $\to$ `Consensus`).
  - Typewriter board terminal console output.
  - Clinical Recommendation object model contracts (`clinicalRecommendation.js`) and Board Session snapshots.
  - 0–100 Evidence Strength Score gauges and breakdown components.
