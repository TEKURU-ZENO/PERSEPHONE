# ADR-004: Structural Causal Counterfactual Projections

## Status
Accepted

## Context
Oncologists evaluating patients must decide between alternative dosing protocols. Standard clinical dashboards display historical curves or basic projections, but do not provide a direct causal comparison of "what would have happened" if a different dosing path was chosen for the exact same patient baseline.

## Decision
We implemented a **Causal Counterfactual Engine** in `simulator.service.js`:
- **Mathematical Framework:** Computes counterfactual potential outcomes $Y(a) = f(X, a, U_Y)$, where $X$ is the patient digital twin baseline, $a$ is the intervention dosing strategy (e.g. MTD vs. Adaptive), and $U_Y$ represents the unobserved microenvironmental factors.
- **Parallel Solvers:** Executes two parallel RK4 trajectories from identical initial boundaries ($SS_0, SR_0$), changing only the intervention parameter.
- **Deltas Calculation:** Computes net gains in Time-to-Progression ($\Delta TTP$), cumulative drug exposure ($\Delta Dose$), and toxicity differences ($\Delta Tox$).

## Consequences
- **Advantages:** Provides actionable clinical decision comparators (factual solid lines vs. counterfactual dashed lines).
- **Disadvantages:** Projections assume a deterministic state transition, which is verified using stochastic walks in the UI but requires further validation against clinical trial databases.
