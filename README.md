# PERSEPHONE: Predictive Evolutionary Reasoning System for Explainable Precision Healthcare & Oncology Network Engine

PERSEPHONE is an evidence-grounded precision oncology decision-support platform. Rather than treating cancer as a static diagnosis, the system mathematically models tumors as dynamic, evolving biological processes characterized by clonal selection, mutation drift, and therapeutic resistance.

---

## 1. Overview
PERSEPHONE implements a complete computational precision oncology pipeline. By conceptualizing cancer as a Darwinian evolutionary process, the platform transitions clinical AI from static diagnostic classification to continuous, longitudinal biomedical intelligence. It integrates high-dimensional genomic sequencing, transcriptomic profiling, multimodal clinical data, and dynamic biomedical knowledge graphs into an advanced agentic reasoning fabric.

---

## 2. Module Fidelity & Implementation Status

To ensure complete scientific transparency and honest labeling, PERSEPHONE categorizes every subsystem and dataset into three distinct tiers:

| Tier | Category | Components & Datasets | Fidelity & Verification Notes |
| :--- | :--- | :--- | :--- |
| **Tier 1** | **Real Data** | • COSMIC v3.4 SBS Mutational Signatures Matrix<br>• Clinical Trials Knowledge Registry | • Authentic 96×86 matrix from COSMIC catalog<br>• IDs and titles checked against ClinicalTrials.gov (Oct 2026); cancer lineages and biomarker eligibility explicitly curated |
| **Tier 2** | **Real Algorithm, Sample Data** | • RK4 Numerical ODE Solver<br>• Lotka-Volterra Clonal Competition Model<br>• NNLS Signature Fitting Engine<br>• Knowledge Graph Pathfinding<br>• Reinforcement Learning Engine (DQN training loop, Actor-Critic evaluation)<br>• Biological Reference Knowledge | • Verified mathematical 4th-order Runge-Kutta numerical integration<br>• Assumed parameters, not fitted to data (reproduces Gatenby's adaptive dynamics)<br>• Exact non-negative least squares optimization<br>• Deterministic depth-first path traversal on relational graphs<br>• Functional RL training & policy inference loops<br>• Sample excerpts and representative fixtures of Reactome, DrugBank, ClinVar, TCGA, CCLE, and GDSC |
| **Tier 3** | **Simulated / Mock Modules** (`is_mock: True`) | • CT Volumetric Segmentor (`ct_segmentor.py`)<br>• MRI Volumetric Segmentor (`mri_segmentor.py`)<br>• Radiomics Feature Extractor (`radiomics.py`)<br>• GradCAM Saliency Heatmap (`gradcam.py`)<br>• Multi-Head Attention Rollout (`attention.py`)<br>• WSI Slide Loader (`wsi_loader.py`)<br>• DICOM / NIfTI Volume Loader (`loader.py`)<br>• Morphology Feature Extractor (`feature_extractor.py`) | • Deterministic simulated pipeline responses flagged explicitly with `is_mock: True`<br>• Real DL imaging models and gigapixel WSI files are not bundled; UI displays simulated state |

---

## 3. Features
- **Clonal Population Dynamics:** Models the Darwinian competition between Treatment-Sensitive ($S_S$) and Treatment-Resistant ($S_R$) tumor clones using competitive Lotka-Volterra equations solved via Runge-Kutta 4th order (RK4) integration.
- **Regimen Scenario Simulator:** Evaluates prospective dosing strategies under potential outcomes framework $Y(a) = f(X, a, U_Y)$ and displays deltas for Time-to-Progression (TTP), cumulative dose, and toxicity.
- **HTML5 Canvas Knowledge Graph:** High-performance, zero-dependency 2D force-directed simulation of bio-clinical relationships with interactive depth-first path tracing.
- **Deterministic Agent DAG:** Sequences clinical decision-making across 5 specialized rule-based agents (`Evolution` $\to$ `Planning` $\to$ `Evidence` $\to$ `Safety` $\to$ `Consensus`) compiling structured recommendations and Evidence Strength scores using deterministic rule-based pipelines (no external LLMs).
- **Audit Trail & Validation Layer:** Formal JSON schema validation models for patient simulation profiles (uncalibrated) and simulation outputs, persisting consensus reports.

---

## 4. Architecture
PERSEPHONE integrates clinical data, continuous-time mathematical models, and biomedical knowledge networks into a unified decision support workstation:

```
Patient Simulation Profile (Uncalibrated)
        │
        ▼
Simulation Profile Operating Environment (DTOE)
        │
        ▼
Tumor Dynamics Simulator (RK4 Solver)
        │
        ▼
Regimen Scenario Simulator
        │
        ▼
Biomedical Knowledge Graph (Oncology KG)
        │
        ▼
Evidence Grounding Layer (Parameter Registry)
        │
        ▼
Evidence-Grounded Tumor Board (Rule-Based Agent DAG)
        │
        ▼
Clinical Recommendation Contract
```

A detailed spec is available in the [ARCHITECTURE.md](./docs/ARCHITECTURE.md) blueprint.

---

## 5. Screenshots

The DTOE workstation UI components are visualized below:
- **Simulation Profile Operating Environment Dashboard:** Displays active profile cards, biometric streams, CA-125 biomarkers, and histopathology slides. [View DTOE Mockup](./docs/screenshots/DTOE.png)
- **Simulation Lab Panel:** Visualizes Runge-Kutta numerical trajectories comparing MTD and Adaptive regimens. [View Simulator Mockup](./docs/screenshots/SimulationLab.png)
- **Knowledge Graph Explorer:** Tracks mutation-to-drug-to-trial associations dynamically. [View Graph Explorer Mockup](./docs/screenshots/GraphExplorer.png)
- **Multi-Agent Tumor Board Console:** Renders stateful DAG nodes and typewriter logs. [View Tumor Board Mockup](./docs/screenshots/TumorBoard.png)

---

## 6. Installation
No package dependencies are required to run the core simulation platform or test suites. Clone the repository and verify local environment requirements as detailed in the [REPRODUCIBILITY.md](./docs/REPRODUCIBILITY.md) protocol.

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

### Running Tests Locally
To run the full end-to-end test suite (`node tests/run-tests.js`), both the Python Scientific Computing Runtime (SCR) and Node gateway must be active:
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
   # Python scientific unit tests
   python -m unittest discover -s backend/python/tests/scientific

   # Node end-to-end integration and verification suite
   node tests/run-tests.js
   ```

---

## 8. Roadmap
We track development progression across 6 chronological milestones:
- **Phase 1: Simulation Profile Operating Environment (DTOE)** (✅ Complete)
- **Phase 2: Tumor Dynamics Simulator & Scenario Projections** (✅ Complete)
- **Phase 3: Knowledge Graph & Evidence Grounding** (✅ Complete)
- **Phase 4: Multi-Agent Tumor Board (DAG)** (✅ Complete)
- **Phase 5: Graph-RAG & Long-Term Memory** (🟡 Active)
- **Phase 6: RL-Based Dose Optimization** (🔵 Planned)

Refer to the [PROJECT_ROADMAP.md](./docs/PROJECT_ROADMAP.md) for full details.

---

## 9. Research Contributions
- **Competitive Coexistence Modeling:** Reproduces Gatenby's adaptive therapy competition dynamics in simulation, demonstrating that keeping a subpopulation of drug-sensitive cells alive via treatment holidays prevents competitive release of resistant populations.
- **Evidence-Grounded Recommendation Score:** Defines an audit-ready scoring model (0-100) combining clinical trial records, publication PMIDs, and safety clearances.
- **Regimen Scenario Projections:** Integrates prospective potential outcomes calculations into real-time clinical dashboards.

---

## 10. Tech Stack
- **Core Workstation:** HTML5, CSS3, Vanilla ES6 JavaScript (zero-dependency).
- **Web Server:** Node.js static HTTP stream.
- **Verification:** Native Node assertions.
- **Orchestration:** Directed Acyclic Graph state models.

---

## 11. License
PERSEPHONE is released under the [MIT License](./LICENSE).
