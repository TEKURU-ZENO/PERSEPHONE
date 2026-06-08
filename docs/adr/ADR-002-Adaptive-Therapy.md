# ADR-002: Rule-Based Adaptive Dosing Engine and Fitness Cost Constraints

## Status
Accepted

## Context
Standard oncology treatment relies on Maximum Tolerated Dose (MTD) to eliminate as many cancer cells as possible. However, in heterogeneous tumors, MTD eliminates the drug-sensitive subpopulation, removing spatial and resource constraints that suppressed the growth of drug-resistant clones (competitive release). We need a model to simulate adaptive dosing strategies that exploit these ecological dynamics.

## Decision
We implemented Gatenby's classic **Rule-Based Adaptive Dosing** algorithm:
- **Dosing Hold:** Chemotherapy/targeted dosing is suspended if the total tumor volume drops below 50% of the baseline volume ($0.5 \times V_0$).
- **Dosing Resumption:** Dosing is resumed at the full MTD dose when the tumor volume rebounds to 100% of baseline volume ($1.0 \times V_0$).
- **Fitness Cost of Resistance:** The resistant clone's growth rate is mathematically penalized ($\alpha_2 < \alpha_1$) to represent the metabolic burden of resistance pathways in the absence of therapeutic selection pressure.

## Consequences
- **Advantages:** Delays time-to-progression (TTP) by maintaining a stable subpopulation of sensitive cells to suppress resistant clone expansion.
- **Disadvantages:** The tumor volume is kept under active monitoring rather than attempting complete eradication, which represents a paradigm shift in clinical strategy.
