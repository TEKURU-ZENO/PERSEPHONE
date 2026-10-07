# PERSEPHONE: Predictive Evolutionary Reasoning System for Explainable Precision Healthcare & Oncology Network Engine

PERSEPHONE is an evidence-grounded precision oncology decision-support platform. Rather than treating cancer as a static diagnosis, the system mathematically models tumors as dynamic, evolving biological processes characterized by clonal selection, mutation drift, and therapeutic resistance.

---

## 1. Overview
PERSEPHONE implements a complete computational precision oncology operating system across 20 completed architectural phases. By conceptualizing cancer as a Darwinian evolutionary process, the platform transitions clinical AI from static diagnostic classification to continuous, longitudinal biomedical intelligence. It coordinates a **23-Agent Collaborative Council** distributed across **5 Intelligence Planes**, integrating high-dimensional genomic sequencing, mutational signature deconvolution, multimodal clinical data, and dynamic biomedical knowledge graphs into a deterministic, audit-ready reasoning fabric.

---

## 2. Module Fidelity & Implementation Status

To ensure complete scientific transparency and honest labeling, PERSEPHONE categorizes every subsystem and dataset into three distinct tiers:

| Tier | Category | Components & Datasets | Fidelity & Verification Notes |
| :--- | :--- | :--- | :--- |
| **Tier 1** | **Real Data** | • COSMIC v3.4 SBS Mutational Signatures Matrix<br>• Clinical Trials Knowledge Registry | • Authentic 96×86 matrix from COSMIC catalog (canonical LF SHA-256 verified)<br>• IDs and titles checked against ClinicalTrials.gov (Oct 2026); cancer lineages and biomarker eligibility explicitly curated |
| **Tier 2** | **Real Algorithm, Sample Data** | • RK4 Numerical ODE Solver<br>• Lotka-Volterra Clonal Competition Model<br>• NNLS Signature Fitting Engine<br>• Knowledge Graph Pathfinding<br>• Reinforcement Learning Engine (DQN training loop, Actor-Critic evaluation)<br>• Biological Reference Knowledge | • Verified mathematical 4th-order Runge-Kutta numerical integration<br>• Assumed parameters, not fitted to clinical benchmark data<br>• Exact non-negative least squares optimization<br>• Deterministic depth-first path traversal on relational graphs<br>• Functional RL training & policy inference loops<br>• Sample excerpts and representative fixtures of Reactome, DrugBank, ClinVar, TCGA, CCLE, and GDSC |
| **Tier 3** | **Simulated / Mock Modules** (`is_mock: True`) | • CT Volumetric Segmentor (`ct_segmentor.py`)<br>• MRI Volumetric Segmentor (`mri_segmentor.py`)<br>• Radiomics Feature Extractor (`radiomics.py`)<br>• GradCAM Saliency Heatmap (`gradcam.py`)<br>• Multi-Head Attention Rollout (`attention.py`)<br>• WSI Slide Loader (`wsi_loader.py`)<br>• DICOM / NIfTI Volume Loader (`loader.py`)<br>• Morphology Feature Extractor (`feature_extractor.py`) | • Deterministic simulated pipeline responses flagged explicitly with `is_mock: True`<br>• Real DL imaging models and gigapixel WSI files are not bundled; UI displays simulated state |

---

## 3. Platform Capabilities & Core Features

Across its 20 development phases, PERSEPHONE delivers a comprehensive clinical workstation:

- **Clonal Population Dynamics (Phase 2):** Models Darwinian competition between Treatment-Sensitive ($S_S$) and Treatment-Resistant ($S_R$) tumor clones using competitive Lotka-Volterra equations solved via Runge-Kutta 4th order (RK4) integration, embedding resistance fitness costs ($\alpha_2 < \alpha_1$).
- **Regimen Scenario Simulator (Phase 2, 17):** Evaluates prospective dosing strategies, displaying comparative deltas for Time-to-Progression (TTP), cumulative drug exposure, and toxicity.
- **Biomedical Knowledge Graph & Graph-RAG v2 (Phase 3, 8):** Zero-dependency HTML5 Canvas 2D force-directed layout engine with depth-first pathfinding, paired with hybrid vector-graph retrieval and clinical grounding gates.
- **Deterministic Rule-Based Decision Pipeline (Phase 4, 11, 17–20):** Sequences clinical deliberation across 23 specialized rule-based modules coordinated via Directed Acyclic Graphs (DAG) and blackboard state contracts (no external LLMs).
- **Multi-Omics Feature Store (Phase 6, 13):** Curated schemas and quality control for TCGA, CCLE, GDSC, ClinVar, and DrugBank, integrated with Non-Negative Least Squares (NNLS) deconvolution against COSMIC v3.4 SBS signatures.
- **Reinforcement Learning Optimization (Phase 9):** `OncologyGymEnv` supporting DQN training loops and Actor-Critic policy evaluations for adaptive dosing holiday discovery.
- **Model Calibration & Uncertainty Bands (Phase 10):** Parametric bootstrap uncertainty quantification for numerical trajectories.
- **Multimodal Diagnostic Lab (Phase 12):** Whole slide imaging (WSI) patch extraction, tumor purity/necrosis metrics, CT/MRI volumetric segmentation, radiomics texture analysis, and GradCAM/Attention interpretability.
- **Clinical Trials Intelligence (Phase 14):** Biomarker and cancer lineage matching grounded in 16 verified ClinicalTrials.gov protocols with automated protein change normalization (`p.Gly12Asp` $\to$ `G12D`) and negative screening logic.
- **Longitudinal Monitoring & Response Kinetics (Phase 15, 16):** RECIST 1.1 radiographic tumor burden tracking, molecular lead-time forecasting, and resistance escape velocity modeling.
- **Clinical Governance & Deterministic Abstention (Phase 19):** Rule engines evaluating KDIGO 2024 (renal), CTCAE v5.0 (toxicity), and CPIC guidelines, with strict reason-coded abstention and Multimodal Discordance Index verification.
- **PERSEPHONE OS Kernel & Control Plane (Phase 20):** Five-plane intelligence architecture, thread-safe `BlackboardMemory`, `OSEventBus` reactive streams, cryptographic `ProvenanceLedger`, SHA-256 sealed `ExperimentManifest`, and high-precision `CaseReplayEngine` (RMSE < 1e-4).

---

## 4. Systems Architecture

PERSEPHONE structures clinical intelligence across **5 Coordinated Intelligence Planes** orchestrated by the **PERSEPHONE OS Kernel**:

```
+=============================================================================+
|                             PERSEPHONE OS KERNEL                            |
|        [PersephoneKernel]   [BlackboardMemory]   [OSEventBus]   [Ledger]     |
+=============================================================================+
        │                   │                   │                   │
        ▼                   ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│     PATIENT     │ │   SCIENTIFIC    │ │    CLINICAL     │ │    EVIDENCE     │
│  INTELLIGENCE   │ │  INTELLIGENCE   │ │  INTELLIGENCE   │ │  INTELLIGENCE   │
│      PLANE      │ │      PLANE      │ │      PLANE      │ │      PLANE      │
├─────────────────┤ ├─────────────────┤ ├─────────────────┤ ├─────────────────┤
│ • Twin Profiles │ │ • RK4 Simulator │ │ • Pharmacogen.  │ │ • Graph-RAG v2  │
│ • Telemetry IoT │ │ • Lotka-Volterra│ │ • Drug Resolver │ │ • Trials Matcher│
│ • Histopath WSI │ │ • NNLS Signatures││ • Response Pred.│ │ • NCCN Guidelines│
│ • Longitudinal  │ │ • RL Optimizer  │ │ • Resistance Map│ │ • Merkle Lineage│
└─────────────────┘ └─────────────────┘ └─────────────────┘ └─────────────────┘
        │                   │                   │                   │
        └───────────────────┴─────────┬─────────┴───────────────────┘
                                      ▼
                        ┌───────────────────────────┐
                        │     GOVERNANCE PLANE      │
                        ├───────────────────────────┤
                        │ • KDIGO 2024 / CTCAE v5.0 │
                        │ • CPIC Guidelines Rules   │
                        │ • Clinical Abstention     │
                        │ • Discordance / ECE Score │
                        └───────────────────────────┘
                                      │
                                      ▼
                        ┌───────────────────────────┐
                        │   CLINICAL RECOMMENDATION │
                        │ (SUPPORTED/CAUTION/ABSTAIN│
                        └───────────────────────────┘
```

A detailed systems specification is available in the [ARCHITECTURE.md](./docs/ARCHITECTURE.md) blueprint.

---

## 5. Workstation UI Panels

The clinical workstation comprises 16 interactive panels mounted in the DTOE interface:
1. **DTOE Workstation (Tab 1):** Active patient simulation cards, biometric streams, CA-125 biomarkers, and tissue slides. [View DTOE Mockup](./docs/screenshots/DTOE.png)
2. **Simulation Lab (Tab 2):** Runge-Kutta numerical trajectories comparing MTD and Adaptive regimens. [View Simulator Mockup](./docs/screenshots/SimulationLab.png)
3. **Knowledge Graph Explorer (Tab 3):** Mutation-to-drug-to-trial relational maps and DFS path tracing. [View Graph Explorer Mockup](./docs/screenshots/GraphExplorer.png)
4. **Tumor Board Console (Tab 4):** Stateful rule-based decision pipeline DAG execution and typewriter logs. [View Tumor Board Mockup](./docs/screenshots/TumorBoard.png)
5. **Clinical Memory Workspace (Tab 5):** In-memory TF-IDF concept retrieval and audit trail inspection.
6. **Patient Simulation Profile Biobank (Tab 6):** Reference cell line and clinical cohort multi-omics feature stores.
7. **Evidence Graph-RAG (Tab 7):** Hybrid vector and graph semantic query interface.
8. **Policy Optimization (Tab 8):** Reinforcement learning training reward curves and policy actions.
9. **Clinical Validation (Tab 9):** Calibration curves and parametric bootstrap confidence intervals.
10. **Clinical AI Runtime (Tab 10):** Provider middleware telemetry, rate limits, and health status.
11. **Multimodal Lab (Tab 11):** Pathology WSI viewer, CT/MRI segmentation, and GradCAM explainability.
12. **Genomic Intelligence (Tab 12):** COSMIC mutational signature deconvolution and variant tiering.
13. **Clinical Trials (Tab 13):** Verified ClinicalTrials.gov search and biomarker eligibility screening.
14. **Clinical Monitoring (Tab 14):** Longitudinal RECIST 1.1 tumor kinetics and molecular lead-time forecasting.
15. **Response Intelligence (Tab 15):** Multimodal response classification and resistance escape predictions.
16. **Regimen Scenario Lab (Tab 16):** Multi-arm synthetic cohort simulation and regimen scenario assumption audit.
17. **Research Intelligence (Tab 17):** Clinical guideline compliance, contradiction detection, and SHA-256 provenance.
18. **Clinical Governance (Tab 18):** Deterministic safety gates (KDIGO, CTCAE, CPIC) and abstention logs.
19. **PERSEPHONE OS Cockpit (Tab 19):** Kernel telemetry, blackboard inspection, event bus log, and manifest replay.

---

## 6. Installation & Environment

### Prerequisites
- **Node.js**: `v18.16.0` or higher (`v20` recommended)
- **Python**: `3.12+` with PyTorch (CPU-only build is sufficient)

Full environment matrix and reproducibility checklists are maintained in [REPRODUCIBILITY.md](./docs/REPRODUCIBILITY.md).

---

## 7. Running Locally

### Workstation Dashboard
1. **Navigate to the Application Directory:**
   ```bash
   cd frontend/apps/dashboard
   ```
2. **Start the HTTP Web Server:**
   ```bash
   node server.js
   ```
3. **Launch the Workstation:**
   Open your browser and navigate to: [http://localhost:3000](http://localhost:3000)

### Running the End-to-End Test & Verification Suites
To execute the comprehensive verification suites (`node tests/run-tests.js`), both the Python Scientific Computing Runtime (SCR) and Node gateway must be active:

1. **Install Python dependencies:**
   ```bash
   pip install torch --index-url https://download.pytorch.org/whl/cpu
   pip install -r backend/python/requirements.txt
   ```
2. **Start Python SCR (Port 5000):**
   ```bash
   PYTHONPATH=. python backend/python/app.py
   ```
3. **Start Node Gateway (Port 3000):**
   ```bash
   node backend/node/server.js
   ```
4. **Execute Verification Suites:**
   ```bash
   # Python scientific unit tests (179 tests)
   python -m unittest discover -s backend/python/tests/scientific

   # Node end-to-end integration and verification suite (37 suites)
   node tests/run-tests.js
   ```

---

## 8. Development Roadmap

All 20 engineering phases are completed, verified, and integrated into the PERSEPHONE OS codebase:
- **Phases 1–4**: Foundational Workstation, RK4 Simulator, Knowledge Graph, 5-Agent DAG (✅ Complete)
- **Phases 5–8**: Memory Workspace, Feature Store, SCR Parity, Graph-RAG v2 (✅ Complete)
- **Phases 9–11**: RL Policy Optimization, Calibration & Uncertainty, CAIR Engine (✅ Complete)
- **Phases 12–14**: Multimodal Imaging, Genomic Intelligence, Clinical Trials Intelligence (✅ Complete)
- **Phases 15–17**: Longitudinal Monitoring, Response Intelligence, Synthetic Cohorts (✅ Complete)
- **Phases 18–20**: Research Intelligence, Clinical Governance, PERSEPHONE OS Capstone Layer (✅ Complete)

Refer to [PROJECT_ROADMAP.md](./docs/PROJECT_ROADMAP.md) for full phase-by-phase documentation.

---

## 9. Research Contributions
- **Clonal Competition Modeling:** Implements Lotka-Volterra competition dynamics between drug-sensitive and resistant subpopulations under treatment pressure (uncalibrated parameters; does not demonstrate clinical adaptive advantage over MTD without patient-specific calibration).
- **Evidence-Grounded Recommendation Score:** Defines an audit-ready scoring model (0–100) combining clinical trial records, publication PMIDs, and safety clearances.
- **Deterministic Multi-Plane Governance:** Implements a small set of safety rules derived from KDIGO, CTCAE, and CPIC guidelines with formal clinical abstention semantics (`SUPPORTED`, `CAUTION`, `ABSTAIN`).
- **Cryptographic Provenance Lineage:** Establishes SHA-256 hash chains for every clinical claim and recommendation, backed by SHA-256 experiment manifest seals.

---

## 10. Tech Stack
- **Core Workstation:** HTML5, CSS3, Vanilla ES6 JavaScript (zero-dependency).
- **Backend Runtime:** Python 3.12 (Scientific Compute Runtime / Flask), PyTorch, NumPy, SciPy.
- **Gateway & Networking:** Node.js native HTTP stream and reverse proxy.
- **Verification Harness:** Native Node assertions and Python `unittest`.
- **Orchestration:** Directed Acyclic Graph state models and Blackboard memory patterns.

---

## 11. License
PERSEPHONE is released under the [MIT License](./LICENSE).
