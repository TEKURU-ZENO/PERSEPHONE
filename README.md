# PERSEPHONE: Predictive Evolutionary Reasoning System for Explainable Precision Healthcare & Oncology Network Engine

PERSEPHONE is an evidence-grounded precision oncology decision-support platform. Rather than treating cancer as a static diagnosis, the system mathematically models tumors as dynamic, evolving biological processes characterized by clonal selection, mutation drift, and therapeutic resistance.

---

## 1. Overview
PERSEPHONE implements a complete computational precision oncology pipeline. By conceptualizing cancer as a Darwinian evolutionary process, the platform transitions clinical AI from static diagnostic classification to continuous, longitudinal biomedical intelligence. It integrates high-dimensional genomic sequencing, transcriptomic profiling, multimodal clinical data, and dynamic biomedical knowledge graphs into an advanced agentic reasoning fabric.

---

## 2. Features
- **Clonal Population Dynamics:** Models the Darwinian competition between Treatment-Sensitive ($S_S$) and Treatment-Resistant ($S_R$) tumor clones using competitive Lotka-Volterra equations solved via Runge-Kutta 4th order (RK4) integration.
- **Causal Counterfactual Engine:** Computes counterfactual potential outcomes $Y(a) = f(X, a, U_Y)$ evaluating alternative dosing strategies and displays deltas for Time-to-Progression (TTP), cumulative dose, and toxicity.
- **HTML5 Canvas Knowledge Graph:** High-performance, zero-dependency 2D force-directed simulation of bio-clinical relationships with interactive depth-first path tracing.
- **Deterministic Agent DAG:** Sequences clinical decision-making across 5 specialized agents (`Evolution` $\to$ `Planning` $\to$ `Evidence` $\to$ `Safety` $\to$ `Consensus`) compiling structured recomendations and Evidence Strength scores.
- **Audit trail & Validation Layer:** Formal JSON schema validation models for digital twins and simulation outputs, persisting consensus reports.

---

## 3. Architecture
PERSEPHONE integrates clinical data, continuous-time mathematical models, and biomedical knowledge networks into a unified decision support workstation:

```
Patient Digital Twin
        │
        ▼
Digital Twin Operating Environment (DTOE)
        │
        ▼
Tumor Dynamics Simulator (RK4 Solver)
        │
        ▼
Causal Counterfactual Engine
        │
        ▼
Biomedical Knowledge Graph (Oncology KG)
        │
        ▼
Evidence Grounding Layer (Parameter Registry)
        │
        ▼
Evidence-Grounded Tumor Board (Agent DAG)
        │
        ▼
Clinical Recommendation Contract
```

A detailed spec is available in the [ARCHITECTURE.md](file:///c:/Users/Dev%20Mehta/Desktop/PERSEPHONE/docs/ARCHITECTURE.md) blueprint.

---

## 4. Screenshots

The DTOE workstation UI components are visualized below:
- **Digital Twin Operating Environment Dashboard:** Displays active twin card profiles, biometric streams, CA-125 CA biomarkers, and histopathology slides. [View DTOE Mockup](file:///c:/Users/Dev%20Mehta/Desktop/PERSEPHONE/docs/screenshots/DTOE.png)
- **Simulation Lab Panel:** Visualizes Runge-Kutta numerical trajectories comparing MTD and Adaptive regimens. [View Simulator Mockup](file:///c:/Users/Dev%20Mehta/Desktop/PERSEPHONE/docs/screenshots/SimulationLab.png)
- **Knowledge Graph Explorer:** Tracks mutation-to-drug-to-trial associations dynamically. [View Graph Explorer Mockup](file:///c:/Users/Dev%20Mehta/Desktop/PERSEPHONE/docs/screenshots/GraphExplorer.png)
- **Multi-Agent Tumor Board Console:** Renders stateful DAG nodes and typewriter typewriter logs. [View Tumor Board Mockup](file:///c:/Users/Dev%20Mehta/Desktop/PERSEPHONE/docs/screenshots/TumorBoard.png)

---

## 5. Installation
No package dependencies are required to run the core simulation platform or test suites. Clone the repository and verify local environment requirements as detailed in the [REPRODUCIBILITY.md](file:///c:/Users/Dev%20Mehta/Desktop/PERSEPHONE/docs/REPRODUCIBILITY.md) protocol.

---

## 6. Running Locally
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

4. **Run Verification Test Suite:**
   To execute the verification checks:
   ```bash
   node tests/run-tests.js
   ```

---

## 7. Roadmap
We track development progression across 6 chronological milestones:
- **Phase 1: Digital Twin Operating Environment (DTOE)** (✅ Complete)
- **Phase 2: Tumor Dynamics Simulator & Counterfactuals** (✅ Complete)
- **Phase 3: Knowledge Graph & Evidence Grounding** (✅ Complete)
- **Phase 4: Multi-Agent Tumor Board (DAG)** (✅ Complete)
- **Phase 5: Graph-RAG & Long-Term Memory** (🟡 Active)
- **Phase 6: RL-Based Dose Optimization** (🔵 Planned)

Refer to the [PROJECT_ROADMAP.md](file:///c:/Users/Dev%20Mehta/Desktop/PERSEPHONE/docs/PROJECT_ROADMAP.md) for full details.

---

## 8. Research Contributions
- **Competitive Coexistence Modeling:** Demonstrates that keeping a subpopulation of drug-sensitive cells alive via treatment holidays prevents competitive release of resistant populations.
- **Evidence-Grounded Recommendation Score:** Defines an audit-ready scoring model (0-100) combining clinical trial records, publication PMIDs, and safety clearances.
- **Causal Counterfactual Projections:** Integrates structural potential outcomes calculations into real-time clinical dashboards.

---

## 9. Tech Stack
- **Core Workstation:** HTML5, CSS3, Vanilla ES6 JavaScript (zero-dependency).
- **Web Server:** Node.js static HTTP stream.
- **Verification:** Native Node assertions.
- **Orchestration:** Directed Acyclic Graph state models.

---

## 10. License
PERSEPHONE is released under the [MIT License](file:///c:/Users/Dev%20Mehta/Desktop/PERSEPHONE/LICENSE).
