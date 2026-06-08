# PERSEPHONE Development Roadmap

This roadmap tracks the development of the PERSEPHONE Precision Oncology Platform.

---

## Roadmap Tracker

### Phase 1: Digital Twin Operating Environment (DTOE)
- **Status:** ✅ Complete
- **Description:** Establish the reactive dashboard workspace, including observable patient state stores, stochastic telemetry generators, CA-125 trackers, and histopathology slide viewer integrations.

### Phase 2: Tumor Dynamics Simulator & Counterfactuals
- **Status:** ✅ Complete
- **Description:** Implement the coupled Runge-Kutta 4th order (RK4) Lotka-Volterra competition model, plasma PK pharmacokinetics, systemic toxicity PD, rule-based adaptive dosing rules, and the structural causal counterfactual evaluation engine.

### Phase 3: Knowledge Graph & Evidence Grounding
- **Status:** ✅ Complete
- **Description:** Deploy the HTML5 Canvas 2D interactive layout explorer with depth-first pathway tracing, establishing direct links between somatic mutations, drug inhibition targets, active clinical trials, and PubMed parameter PMIDs.

### Phase 4: Multi-Agent Tumor Board (DAG)
- **Status:** ✅ Complete
- **Description:** Orchestrate the stateful Directed Acyclic Graph (DAG) sequence (`Evolution` $\to$ `Planning` $\to$ `Evidence` & `Safety` $\to$ `Consensus`), computing weighted Evidence Strength scores and outputting scrollable typewriter terminal logs.

### Phase 5: Graph-RAG & Long-Term Memory
- **Status:** 🟡 Active
- **Description:** Introduce persistent database storage for board sessions, query parsers linking historical audit trails (`audit/recommendations/`), and vector embeddings matched to Knowledge Graph nodes for semantic retrieval.

### Phase 6: RL-Based Dose Optimization
- **Status:** 🔵 Planned
- **Description:** Integrate Deep Q-Network (DQN) agents into the simulation environment to optimize treatment holiday cycles, comparing RL-derived therapeutic actions against standard MTD and adaptive protocols.
