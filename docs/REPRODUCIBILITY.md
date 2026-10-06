# Reproducibility Protocol & Environment Matrix

This protocol details the technical specifications, versions, verification procedures, and mathematical tolerances required to replicate the simulations, pathfinding algorithms, 23-agent council debates, and PERSEPHONE OS kernel operations across all 20 implemented phases.

---

## 1. System Environment Matrix

To ensure bit-level numerical reproducibility and identical decision trajectories, verify that your local environment satisfies:

| Dependency | Verified Version | Requirement Type | Notes |
| :--- | :--- | :--- | :--- |
| **Node.js** | `v18.16.0` or `v20.x` | Required (Gateway & UI) | Zero-dependency ES6 module runner, native HTTP stream, test coordinator. |
| **Python** | `3.12.x` | Required (SCR Backend) | Scientific Computing Runtime executing ODE solvers, RL policies, and NNLS fitting. |
| **PyTorch** | `2.x+` (CPU Build) | Required (RL & Models) | CPU build is sufficient (`torch --index-url https://download.pytorch.org/whl/cpu`). |
| **NumPy / SciPy** | `1.26+` / `1.12+` | Required (Scientific) | Numerical matrix computations and NNLS optimization routines. |
| **Web Browser** | Chrome `114+`, Safari `16.5+` | Required (Frontend) | Standard ES6 Module and HTML5 Canvas support required. |

---

## 2. Scientific Parameter Grounding & Hash Invariants

### 1. Mathematical Simulation Parameters
All ODE and pharmacokinetic parameters reside in [parameter-registry.json](../research/parameter-registry.json):
- Proliferation Rate $\alpha_1$: `0.08` day$^{-1}$
- Resistance Fitness Cost Rate $\alpha_2$: `0.045` day$^{-1}$ ($\alpha_2 < \alpha_1$)
- Carrying Capacity $K$: `200.0` cm$^3$
- Elimination constant $k_e$: `0.15` day$^{-1}$
- Toxicity accumulation $\beta$: `0.10`, clearance $\gamma$: `0.08`

### 2. Mutational Signatures Reference Invariant
The reference matrix for COSMIC v3.4 SBS96 deconvolution is located at `datasets/reference/cosmic_sbs96_reference.csv`:
- **Matrix Dimensions:** 96 mutation channels $\times$ 86 curated signatures
- **Canonical LF SHA-256 Checksum:**
  ```
  aad0be68be61cb94674d8c5c01309f7ab9670cfcd610966d00b3f0883feeec72
  ```

### 3. Verified Clinical Trials Parity Invariant
All 16 authentic ClinicalTrials.gov records in `datasets/knowledge/verified_trials.json` are mirrored with 100% parity into `frontend/apps/dashboard/src/data/verified-trials.js`. Zero synthetic or fallback trial IDs exist in compute engines.

---

## 3. Step-by-Step Codebase Verification Workflow

### Step 1: Verify Codebase Syntax Integrity
```bash
# Verify syntax correctness across all JavaScript files
git ls-files "*.js" | ForEach-Object { node --check $_ }
```

### Step 2: Run Python Scientific Unit Tests (177 Tests)
```bash
# Execute full scientific unit test suite (ODE, PK/PD, RL, Pharmacogenomics, Trials, OS Kernel)
python -m unittest discover -s backend/python/tests/scientific -v
```

### Step 3: Run Consistency & Parity Enforcement (12 Tests)
```bash
# Verify trial registry parity, COSMIC hash, biomarker tiering, and zero-fallback contracts
python -m unittest backend/python/tests/scientific/test_drug_target_consistency.py -v
```

### Step 4: Start Microservices for End-to-End Integration
Open two terminal instances or start background processes:
```bash
# Terminal 1: Start Python Scientific Compute Runtime (Port 5000)
PYTHONPATH=. python backend/python/app.py

# Terminal 2: Start Node Gateway (Port 3000)
node backend/node/server.js
```

### Step 5: Execute Complete 37-Suite Integration Runner
```bash
# Run complete test runner verifying all 20 phases and performance benchmarks
node tests/run-tests.js
```

Expected result:
```
Total Execution Time: ~10,000 ms
Passed Suites:        37 / 37
Status:               ALL TESTS PASSED (100% REPRODUCIBILITY STATUS)
```

---

## 4. Launching the DTOE Clinical Workstation
To interact with the clinical user interface locally:
```bash
cd frontend/apps/dashboard
node server.js
```
Navigate to [http://localhost:3000](http://localhost:3000) in any modern browser.
