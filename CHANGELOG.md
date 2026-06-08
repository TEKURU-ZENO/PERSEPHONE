# Changelog

All notable changes to the PERSEPHONE platform will be documented in this file.

---

## [1.0.0-RC1] - 2026-06-05

### Added
- **Phase 1 — Digital Twin Operating Environment (DTOE):**
  - Renders Palantir-style header metrics and responsive workstation grids.
  - Decoupled patient record system (`patients.js`) and observable state controller (`patient.store.js`).
  - Integrated IoT biometric simulator with stochastic walks.
  - Synthesized high-resolution tissue slide and scanning overlay.
- **Phase 2 — Tumor Dynamics Simulation Engine:**
  - Coded Fourth-Order Runge-Kutta (RK4) numerical ODE solver.
  - Coupled Lotka-Volterra competition dynamics ($S_S$ vs $S_R$), introducing the resistance fitness cost ($\alpha_2 < \alpha_1$).
  - Integrated Pharmacokinetics and Toxicity accumulation models.
  - Coded rule-based Adaptive Therapy logic (dosing holds at 50%, resume at 100%).
  - Causal Counterfactual Engine comparing alternative dosing projections.
- **Phase 3 — Biomedical Knowledge Graph Explorer:**
  - Decoupled constants into the literature-linked Parameter Registry database.
  - Interactive canvas-based force-directed 2D Knowledge Graph explorer mapping mutations to clinical trials.
  - Integrated context-aware parameter evidence tooltips.
- **Phase 4 — Evidence-Grounded Tumor Board (Deterministic DAG):**
  - Stateful 5-agent DAG orchestrator execution service (`Evolution` → `Planning` → `Evidence` → `Safety` → `Consensus`).
  - Renders a typewriter board Terminal console log output and visual DAG pulsing node checks.
  - Formulated Clinical Recommendation object model contracts (`clinicalRecommendation.js`) and Board Session snapshots (`boardSession.js`).
  - Integrated 0-100 Evidence Strength Score gauges and breakdown components.
