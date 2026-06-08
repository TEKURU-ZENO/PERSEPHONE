# Reproducibility Protocol & Environment Matrix

This protocol details the technical specifications, versions, and validation workflows required to replicate the simulations, pathfinding algorithms, and multi-agent DAG debates in the PERSEPHONE environment.

---

## 1. System Environment Matrix

To ensure identical numerical outcomes for the Runge-Kutta 4th order (RK4) solver, verify that your local environment satisfies:

| Dependency | Verified Version | Requirement Type | Notes |
| :--- | :--- | :--- | :--- |
| **Node.js** | `v18.16.0` (or higher v18/v20) | Required (Core runtime) | Runs HTTP server and tests. |
| **NPM** | `v9.5.1` | Optional | Not required for execution (zero-dependency). |
| **Web Browser** | Google Chrome `v114+`, Safari `v16.5+` | Required (Frontend) | Standard ES6 Module support required. |
| **Docker** | `v20.10.22+` | Optional (Deployment) | Configured in `docker-compose.yml`. |

---

## 2. Codebase Reproducibility Checklist

### Step 1: Clone and Verify Workspace
Ensure the root directory contains the zero-dependency structure:
```bash
# Check syntax correctness across all modules
find . -name "*.js" -not -path "*/node_modules/*" | xargs -I {} node --check {}
```

### Step 2: Scientific Parameter Grounding
All mathematical parameters reside in [parameter-registry.json](file:///c:/Users/Dev%20Mehta/Desktop/PERSEPHONE/research/parameter-registry.json). The solver reads these constants for patient calculations:
- Proliferation Rate $\alpha_1$: `0.08`
- Fitness Cost Rate $\alpha_2$: `0.045`
- Carrying Capacity $K$: `200.0`
- Efficacy coefficients ($E_S, E_R$) and pharmacokinetic parameters.

### Step 3: Run the Verification Suite
To confirm that numerical solvers, graph pathfinding, and agent DAG execution behaviors align with target values, execute the central test runner:
```bash
node tests/run-tests.js
```

### Step 4: Launching the DTOE Workstation
To host the DTOE clinical dashboard locally:
```bash
cd frontend/apps/dashboard
node server.js
```
Open [http://localhost:3000](http://localhost:3000) in a modern web browser.
