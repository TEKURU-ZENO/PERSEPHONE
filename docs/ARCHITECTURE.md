# PERSEPHONE: Systems Architecture Blueprint

PERSEPHONE is an evidence-grounded Precision Oncology Decision Support System. This document details the technical details, mathematical equations, data schemas, and pipeline contracts governing the platform.

---

## 1. System Architecture Overview

PERSEPHONE is decoupled into three layers:
1. **Digital Twin Operating Environment (DTOE):** A reactive clinical workstation served over Node.js.
2. **Mathematical Simulation Engine:** An ODE solver utilizing Runge-Kutta 4th order integration.
3. **Cognitive Agent Fabric:** A stateful Directed Acyclic Graph (DAG) coordinating specialist clinical agents.

```
+--------------------------------------------------------------+
|             DTOE Workstation (HTML5/CSS3/Vanilla JS)         |
|  [Mission Control]  [Fidelity Gauges]  [Simulation Controls]  |
+----------------------------------------------+---------------+
                                               | (User Settings / Swaps)
                                               v
+--------------------------------------------------------------+
|                     State Store & Services                   |
|   - patient.store.js       - simulator.service.js            |
|   - graph.service.js       - tumor.board.service.js          |
+----------------------------------------------+---------------+
                                               | (RK4 Projections & subgraphs)
                                               v
+--------------------------------------------------------------+
|              Stateful Agent DAG (ai/orchestrator/)           |
|  [Evolution] -> [Planning] -> [Evidence] & [Safety] -> [Consensus] |
+--------------------------------------------------------------+
```

---

## 2. DTOE Workstation & Telemetry
The frontend dashboard acts as the **Digital Twin Operating Environment**:
- **Observable Store:** Implemented in [patient.store.js](file:///c:/Users/Dev%20Mehta/Desktop/PERSEPHONE/frontend/apps/dashboard/src/state/patient.store.js), managing active patient state and subscribing visual panels.
- **Biometric Telemetry:** Simulates real-time patient status with stochastic walks (Brownian motion fluctuation) around baseline heart rate and temperature.
- **Histopathology Slides:** Integrated panel displaying PNG scans served by the Express-like static Node server.

---

## 3. Mathematical Tumor Simulator (RK4)
Models clonal dynamics between sensitive ($S_S$) and resistant ($S_R$) cells using competitive Lotka-Volterra equations:

$$\frac{dS_S}{dt} = \alpha_1 S_S \left(1 - \frac{S_S + S_R}{K}\right) - d(t) \cdot E_S \cdot S_S$$
$$\frac{dS_R}{dt} = \alpha_2 S_R \left(1 - \frac{S_S + S_R}{K}\right) - d(t) \cdot E_R \cdot S_R$$

### Drug PK & Toxicity
- **Pharmacokinetics (PK):** Single-compartment plasma concentration clearance:
  $$\frac{dd}{dt} = \text{Dose}(t) - k_e \cdot d$$
- **Toxicity PD:** Systemic side-effects accumulation:
  $$\frac{dT}{dt} = \beta \cdot d - \gamma \cdot T$$

---

## 4. Causal Counterfactual Engine
Calculates potential outcomes for alternative drug administration strategies:

$$Y(a) = f(X, a, U_Y)$$

The simulator runs both factual ($a = \text{Selected}$) and counterfactual ($a' = \text{Alternative}$) trajectories simultaneously, rendering a comparison of cumulative dose, toxicity, and Time-to-Progression (TTP) deltas.

---

## 5. Biomedical Knowledge Graph
Represents relational bio-clinical data as nodes and edges. Pathfinding is implemented via a depth-first traversal utility (`GraphService.findCausalPathForPatient`), isolating patient-specific subgraphs:
- **Node Types:** Patient, Gene, Mutation, Pathway, Drug, ClinicalTrial, Toxicity.
- **Edge Types:** `has_mutation`, `associated_with`, `targets`, `inhibits`, `causes`, `enrolls`.

---

## 6. Multi-Agent DAG Orchestrator
Sequences patient profiles, simulations, and graph paths across 5 specialized agents:

```
  [Tumor Evolution Agent] 
           │
           ▼
  [Therapy Planning Agent]
      /         \
     v           v
[Evidence Agent] [Safety Agent]
     \           /
      v         v
[Clinical Recommendation Agent]
```

- **Evidence Strength Score (0-100):** Weighted combination of PubMed Citations (30%), Trial matches (25%), Knowledge Graph support (20%), Simulation agreement (15%), and clearance safety verification (10%).

---

## 7. Future Directions
- **Phase 5: Graph-RAG & Long-Term Memory:** Embedding audit trails (`audit/recommendations/`) and querying them using vector indexing linked to the Knowledge Graph nodes.
- **Phase 6: RL-Based Dose Optimization:** Substituting rule-based adaptive holds with a Deep Q-Network (DQN) agent optimizing dose timing based on simulated patient twin feedback.
