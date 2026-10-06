# PERSEPHONE: Systems Architecture Blueprint

PERSEPHONE is an evidence-grounded Precision Oncology Decision Support System. This document details the technical specifications, mathematical equations, data schemas, pipeline contracts, and operational planes governing the platform across all 20 implemented phases.

---

## 1. System Architecture Overview: The 5-Plane Operating System

PERSEPHONE structures precision oncology intelligence across **5 Coordinated Intelligence Planes** orchestrated by the **PERSEPHONE OS Kernel**:

```
+===========================================================================================+
|                                    PERSEPHONE OS KERNEL                                   |
|   • PersephoneKernel (DAG Scheduler)         • BlackboardMemory (Thread-Safe State)       |
|   • OSEventBus (Pub/Sub Event Stream)        • ProvenanceLedger (Merkle Causal Chain)     |
|   • ExperimentManifest (SHA-256 Sealed)      • CaseReplayEngine (RMSE < 1e-4)             |
+===========================================================================================+
        │                           │                           │
        ▼                           ▼                           ▼
┌─────────────────────────┐ ┌─────────────────────────┐ ┌─────────────────────────┐
│     PATIENT PLANE       │ │    SCIENTIFIC PLANE     │ │     CLINICAL PLANE      │
├─────────────────────────┤ ├─────────────────────────┤ ├─────────────────────────┤
│ • Patient Digital Twins │ │ • RK4 Lotka-Volterra ODE│ │ • Pharmacogenomics (CPIC│
│ • Stochastic IoT Stream │ │ • Scenario Simulator    │ │ • Drug-Gene Resolvers   │
│ • Pathology WSI Viewer  │ │ • NNLS COSMIC SBS Engine│ │ • Resistance Escape     │
│ • Longitudinal Kinetics │ │ • RL (DQN + Actor-Critic│ │ • Multimodal Fusion     │
└─────────────────────────┘ └─────────────────────────┘ └─────────────────────────┘
        │                           │                           │
        └───────────────────────────┼───────────────────────────┘
                                    ▼
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│                                  EVIDENCE INTELLIGENCE PLANE                              │
├───────────────────────────────────────────────────────────────────────────────────────────┤
│ • Graph-RAG v2 Hybrid Retrieval (Vector + Graph)                                         │
│ • 16-Trial Verified ClinicalTrials.gov Registry & Biomarker Matcher                      │
│ • Clinical Guidelines Engine (NCCN, ASCO, ESMO) with Temporal Validity & Contradictions  │
│ • Grounding Gate (Rejects unreferenced clinical claims)                                  │
└───────────────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│                                       GOVERNANCE PLANE                                    │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ • Deterministic Safety Rule Engines: KDIGO 2024 (Renal), CTCAE v5.0 (Tox), CPIC (PGx)    │
│ • Clinical Abstention Engine (4 Strict Reason Codes: Contradiction, Toxicity, Discordance)│
│ • Multimodal Discordance Index & Epistemic Uncertainty Calibration (ECE / Brier)         │
│ • Governance Decision Contract: SUPPORTED | CAUTION | ABSTAIN                            │
└───────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core OS Kernel & State Management

The operational core is defined under `backend/python/compute/os/`:
- **`ClinicalCaseContext`:** Authoritative atomic data structure binding patient demographics, somatic mutations, copy-number variations, histology, prior treatments, and organ lineage.
- **`BlackboardMemory`:** Thread-safe state blackboard storing shared inference artifacts with strict type-contract validation (`BlackboardKeyContract`). Keys like `TOP_TRIAL` safely accept `None` when zero trials match biomarker profiles.
- **`OSEventBus`:** Non-blocking publish-subscribe event broker coordinating reactive notifications across agents and telemetry streams.
- **`ProvenanceLedger`:** Append-only cryptographic ledger linking every intermediate deduction to its parent evidence via SHA-256 Merkle nodes.
- **`PersephoneKernel`:** Deterministic DAG scheduler executing council agents with 3-tier failure containment (Fallback, Quarantine, Safe Abstention).
- **`ExperimentManifest` & `CaseReplayEngine`:** Schema v1.0 manifest with SHA-256 seal. Guarantees bit-level identical scientific replay of ODE trajectories and governance decisions with RMSE $< 1\times 10^{-4}$.

---

## 3. Mathematical Tumor Simulation Engine (RK4)

Models Darwinian clonal competition between drug-sensitive ($S_S$) and drug-resistant ($S_R$) subpopulations using coupled competitive Lotka-Volterra differential equations:

$$\frac{dS_S}{dt} = \alpha_1 S_S \left(1 - \frac{S_S + S_R}{K}\right) - d(t) \cdot E_S \cdot S_S$$
$$\frac{dS_R}{dt} = \alpha_2 S_R \left(1 - \frac{S_S + S_R}{K}\right) - d(t) \cdot E_R \cdot S_R$$

### Biological Parameters & Invariants
- $\alpha_1$: Sensitive clone intrinsic proliferation rate (e.g. `0.08` day$^{-1}$).
- $\alpha_2$: Resistant clone intrinsic proliferation rate, enforcing the **fitness cost of resistance** ($\alpha_2 < \alpha_1$, e.g. `0.045` day$^{-1}$).
- $K$: Environmental carrying capacity (`200.0` cm$^3$).
- $E_S, E_R$: Drug kill efficacy coefficients ($E_S \gg E_R$).

### Pharmacokinetics (PK) & Toxicity (PD)
- **Plasma Concentration PK:** Single-compartment clearance:
  $$\frac{dd}{dt} = \text{Dose}(t) - k_e \cdot d$$
- **Systemic Toxicity PD:** Cumulative organ toxicity dynamics:
  $$\frac{dT}{dt} = \beta \cdot d - \gamma \cdot T$$

### Regimen Scenario Simulator
Simulates prospective outcomes $Y(a) = f(X, a, U_Y)$ comparing standard Maximum Tolerated Dose (MTD) against rule-based Adaptive Therapy (suspending dose at 50% tumor volume reduction and resuming at 100% baseline rebound), rendering comparative Time-to-Progression (TTP), dose savings, and toxicity deltas.

---

## 4. Multi-Omics Feature Store & Mutational Signature Deconvolution

Ingests structured biological databases under `datasets/`:
- **COSMIC v3.4 SBS Matrix:** Authentic 96-channel single base substitution reference matrix across 86 curated mutational signatures.
- **NNLS Mutational Signature Deconvolution:** Solves the non-negative least squares optimization problem:
  $$\min_{w \ge 0} \| M - S w \|_2^2$$
  where $M$ is the 96-trinucleotide patient mutation count vector, $S$ is the COSMIC signature matrix, and $w$ is the signature exposure weights.
- **Reference Catalogues:** Curated fixtures for TCGA (ovarian clinical cohort), CCLE (cancer cell line expression), GDSC (drug sensitivity IC50 values), ClinVar (pathogenicity), DrugBank (drug targets), and Reactome (biological pathways).

---

## 5. Biomedical Knowledge Graph & Graph-RAG v2

- **Interactive 2D Canvas Explorer:** Zero-dependency HTML5 Canvas force-directed graph running 60 FPS spring-damper physics, tracing patient-specific paths from mutations to drug targets, clinical trials, and PMIDs.
- **Graph-RAG v2 Hybrid Engine:** Combines dense embedding cosine similarity search with multi-hop relational graph traversal. Entity resolution links somatic variants to canonical NCBIGene and ClinVar identifiers, verified by the clinical Grounding Gate.

---

## 6. The 23-Agent Collaborative Council

PERSEPHONE orchestrates a 23-agent multi-agent council using deterministic rule-based algorithms (no non-deterministic external LLMs):

```
1.  EvolutionAgent             - Clonal population kinetics and TTP projection
2.  TherapyPlannerAgent        - Regimen scheduling and dosing holiday protocols
3.  EvidenceAgent              - PubMed literature grounding and trial linkage
4.  SafetyAgent                - Toxicity thresholds and organ clearance evaluation
5.  ConsensusAgent             - 0-100 Evidence Strength Score and synthesis
6.  GenomicsAgent              - Somatic variant pathogenicity and Tier classification
7.  PharmacologyAgent          - PK clearance and pharmacodynamic interactions
8.  ImagingAgent               - Volumetric CT/MRI and pathology morphology scoring
9.  TrialsAgent                - ClinicalTrials.gov eligibility and negative screening
10. MonitoringAgent            - Longitudinal RECIST 1.1 tracking and escalation rules
11. PathologyAgent             - WSI tumor purity and necrosis estimations
12. RadiologyAgent             - RECIST lesion diameter and radiomics profiling
13. MolecularAgent             - ctDNA variant allele fraction lead-time analysis
14. BiomarkerAgent             - Composite score synthesis and immune signatures
15. MultiOmicsAgent            - Multi-platform data integration
16. ResistanceAgent            - Secondary resistance mechanism forecasting
17. ToxicityAgent              - Organ-specific CTCAE v5.0 grading
18. GuidelineAgent             - NCCN/ASCO/ESMO guideline conformance checking
19. EpistemicAgent             - Uncertainty calibration (ECE / Brier metrics)
20. ProtocolAgent              - Clinical trial protocol feasibility assessment
21. CounterfactualResearchAgent- Multi-arm synthetic twin cohort simulation (Phase 17)
22. ResearchIntelligenceAgent - Guideline contradictions & Merkle lineage (Phase 18)
23. GovernanceAgent            - Deterministic clinical abstention & KDIGO rules (Phase 19)
```

---

## 7. Clinical Safety, Governance & Deterministic Abstention

Under `backend/python/compute/clinical_safety/` and `compute/os/contracts/`:
- **Deterministic Rule Evaluators:**
  - **KDIGO 2024:** Staging acute kidney injury by baseline eGFR and serum creatinine.
  - **CTCAE v5.0:** Grading hematologic, hepatic, and renal toxicities (Grades 1–4).
  - **CPIC Guidelines:** Evaluating DPYD, TPMT, and UGT1A1 metabolizer phenotypes for severe drug contraindications.
- **Clinical Abstention Engine:** Automatically forces an `ABSTAIN` status with transparent reason codes:
  1. `REASON_SEVERE_CONTRAINDICATION`: Toxicological risk exceeds safety boundary.
  2. `REASON_EVIDENCE_CONTRADICTION`: Conflicting guideline directives detected.
  3. `REASON_MULTIMODAL_DISCORDANCE`: Radiologic and molecular trajectories conflict ($MDI > 0.65$).
  4. `REASON_EXCESSIVE_UNCERTAINTY`: Epistemic uncertainty band too wide.

---

## 8. Frontend DTOE Workstation (16 Integrated Panels)

The client workstation is implemented in modular vanilla ES6 JavaScript:
- **Observable State Store:** Implemented in [patient.store.js](../frontend/apps/dashboard/src/state/patient.store.js), broadcasting reactive updates to all active panels.
- **16 Interactive Tab Panels:** Mounted in [TumorBoard.js](../frontend/apps/dashboard/src/components/tumor-board/TumorBoard.js) and coordinated via [Dashboard.js](../frontend/apps/dashboard/src/pages/Dashboard.js).
- **Zero-Dependency Guarantee:** No external frameworks, build tools, or runtime dependencies required for the client application.
