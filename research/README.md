# Research Simulation Models & Parameter Grounding

This directory houses the mathematical foundations, biological parameters, and synthetic research tools of the PERSEPHONE platform.

---

## Components

### 1. Literature Parameter Registry (`parameter-registry.json`)
- Central ground-truth database of mathematical and biological constants for all simulation models.
- Links proliferation rates ($\alpha_1, \alpha_2$), carrying capacity ($K$), and pharmacokinetic coefficients ($k_e, \beta, \gamma$) directly to published PubMed PMIDs.
- Formally enforces the **fitness cost of resistance**: $\alpha_2 < \alpha_1$ across all cancer types.

### 2. Coupled Lotka-Volterra Clonal Competition Model (Phase 2)
- Solved via Fourth-Order Runge-Kutta (RK4) integration with adaptive step size:
  $$\frac{dS_S}{dt} = \alpha_1 S_S \left(1 - \frac{S_S + S_R}{K}\right) - d(t) E_S S_S$$
  $$\frac{dS_R}{dt} = \alpha_2 S_R \left(1 - \frac{S_S + S_R}{K}\right) - d(t) E_R S_R$$
- Evaluates Maximum Tolerated Dose (MTD) vs. threshold-based adaptive dosing protocol (dose suspension at 50% tumor regression, resumption at 100% baseline rebound; uncalibrated parameters do not confer adaptive survival advantage).

### 3. Synthetic Cohort & Counterfactual Research Platform (Phase 17)
- Multi-arm in-silico clinical trial simulation across parameterized patient cohorts.
- Implements the Potential Outcomes framework $Y(a) = f(X, a, U_Y)$ with formal causal assumption manifests, Kaplan-Meier survival curves, and statistical power calculations.
