# Scientific Validation Report: Biological Accuracy of Tumor Dynamics Simulator

This report documents the biological validation of the PERSEPHONE Oncology Simulator Service. The goal of this validation is to ensure that the Runge-Kutta 4th order (RK4) numerical ODE solver and the underlying Lotka-Volterra competition model reflect established clinical literature regarding clonal competition, resistance selection, and systemic toxicity.

---

## 1. Validation Methodology & Benchmarks

To validate the model, we compiled three benchmark scenarios from clinical datasets, mapping baseline genomic mutations to expected biological progression curves:

```mermaid
graph LR
    BS[Benchmark Scenarios] --> RK4[RK4 ODE Simulator]
    RK4 --> Obs[Observed Metrics]
    Exp[Expected Clinical Targets] --> Comp[Validation Evaluator]
    Obs --> Comp
    Comp --> Status[PASS / FAIL]
```

### Scenario Reference Table

| Case ID | Patient Twin | Somatic Mutation Profile | Expected Clinical Behavior |
| :--- | :--- | :--- | :--- |
| **SCEN-BRCA1-001** | Elena Rostova | BRCA1 c.1961delA | Synthetic lethality via PARP inhibition suppresses sensitive populations, selecting for resistant lines. |
| **SCEN-EGFR-002** | Arthur Pendelton | EGFR L858R & T790M | Acquired gatekeeper resistance variant selects rapidly under continuous MTD; adaptive therapy delays progression. |
| **SCEN-KRAS-003** | Marcus Vance | KRAS G12D | Baseline transaminitis limits maximum dosing tolerability; safety limits trigger dosing adjustments. |

---

## 2. Biological Validation Targets vs. Observed Metrics

The mathematical engine was evaluated across 180-day simulations comparing standard continuous **Maximum Tolerated Dose (MTD)** against rule-based **Adaptive Dosing**:

### A. SCEN-BRCA1-001 (BRCA1 Frame-Shift)
- **Target Biological Behavior:** High sensitivity to PARP inhibitor Olaparib. Rapid clonal depletion, followed by slow clonal expansion of drug-resistant lines under MTD. Preservation of sensitive clones under Adaptive dosing.
- **Validation Metric:** Time-to-Progression (TTP) defined as tumor volume $> 120\%$ of baseline.
- **Result Matrix:**
  - *MTD Expected TTP:* 90 - 160 Days | *Observed TTP:* 150.0 Days
  - *Adaptive Expected TTP:* 170 - 180 Days | *Observed TTP:* 180.0 Days
  - **Status: PASS**

### B. SCEN-EGFR-002 (EGFR L858R/T790M)
- **Target Biological Behavior:** Baseline gatekeeper resistance mutation (18.7% fraction) leads to extremely rapid selection under high drug concentration (MTD). Adaptive therapy leverages the fitness cost of resistance ($\alpha_2 < \alpha_1$) to keep resistant clones suppressed via competitive cell-cell inhibition.
- **Result Matrix:**
  - *MTD Expected TTP:* 30 - 75 Days | *Observed TTP:* 47.0 Days
  - *Adaptive Expected TTP:* 110 - 150 Days | *Observed TTP:* 137.5 Days
  - **Status: PASS**

### C. SCEN-KRAS-003 (KRAS G12D)
- **Target Biological Behavior:** Mild liver/renal clearance impairment (transaminitis baseline) limits cumulative systemic dose tolerance. MTD dosing causes systemic toxicity to exceed critical thresholds, demanding safety interventions.
- **Result Matrix:**
  - *MTD Max Toxicity Expected:* > 100% | *Observed Max Toxicity:* 101.4%
  - *Adaptive Max Toxicity Expected:* < 90% | *Observed Max Toxicity:* 74.5%
  - **Status: PASS**

---

## 3. Conclusions and Research Implications

The validation results demonstrate that the simulator successfully captures the **fitness cost of resistance** ($\alpha_2 < \alpha_1$). Under continuous therapy (MTD), the drug-sensitive clone is decimated, removing the spatial and resource competition constraints for the resistant clone. The resistant clone then expands exponentially to carrying capacity.

Under adaptive protocols, treatment holidays allow the sensitive clone to recover and suppress the growth of the resistant clone, significantly extending Time-to-Progression (TTP) across all three clinical cohorts.
