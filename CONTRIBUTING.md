# Contributing Guidelines

Thank you for contributing to the PERSEPHONE Precision Oncology Platform. To maintain research-grade reproducibility, clinical accuracy, and architectural integrity across all 20 phases, please adhere to these guidelines.

---

## 1. Branch Naming Conventions
To keep the git history clean, please name branches according to their architectural target:
- `feature/[subsystem]-[description]` (e.g., `feature/trials-negative-screening`, `feature/rl-actor-critic`)
- `bugfix/[issue-description]` (e.g., `bugfix/kras-g12d-mismatch`, `bugfix/rk4-divergence`)
- `refactor/[component-name]` (e.g., `refactor/policy-loader-cleanup`)

---

## 2. Commit Message Patterns
Commit messages must follow the Conventional Commits specification:
- `feat(trials): implement organ lineage filtering and negative screening`
- `fix(genomics): normalize 3-letter protein changes to standard nomenclature`
- `refactor(rl): replace PPO with Actor-Critic policy network`
- `test(parity): enforce 100% parity between JSON and JS trial registries`
- `docs(blueprint): update ARCHITECTURE.md with 5-plane OS specifications`

---

## 3. Pull Request (PR) Workflow
1. Branch off the `main` development line.
2. Ensure mathematical and biological parameters are grounded in [parameter-registry.json](./research/parameter-registry.json).
3. Add unit test suites validating your changes:
   - Python unit tests under `backend/python/tests/scientific/`
   - Node integration tests under `tests/integration/` (if modifying cross-service APIs)
4. Verify that all test suites pass locally before submitting:
   ```bash
   # 1. Check JavaScript syntax
   git ls-files "*.js" | ForEach-Object { node --check $_ }

   # 2. Run Python scientific tests
   python -m unittest discover -s backend/python/tests/scientific -v

   # 3. Run full integration runner (with live SCR and Node Gateway)
   node tests/run-tests.js
   ```

---

## 4. Coding Standards

### Zero Client Dependency Constraint
- The core workstation frontend and Node gateway must remain **zero-dependency**. Do not add client-side bundling packages, UI frameworks, or assert libraries to `package.json`.
- Rely strictly on native ES6 browser APIs and Node's built-in modules (`fs`, `path`, `http`, `assert`).

### Python Scientific Computing Standards
- Python code under `backend/python/` must target Python 3.12+ with explicit type hints.
- Keep PyTorch dependencies compatible with CPU-only execution (`torch --index-url https://download.pytorch.org/whl/cpu`).
- Simulated or heuristic deep learning models must be explicitly flagged with `is_mock: True`.

### Scientific & Clinical Integrity Rules
- **Physical Boundary Constraints:** ODE state variables (cell populations, drug concentration, cumulative toxicity) cannot drop below zero (`Math.max(0, val)` / `np.clip(val, 0, None)`).
- **Resistance Fitness Cost:** Resistant clone growth rates must be strictly lower than sensitive clone rates in the absence of drug pressure ($\alpha_2 < \alpha_1$).
- **Trial Verification Integrity:** All clinical trial NCT IDs must exist in the verified registry (`datasets/knowledge/verified_trials.json`). Never inject fallback or synthetic trial identifiers.
- **Relative Markdown Links:** All documentation links must use repository-relative paths (`./...` or `../...`), never local `file:///` URIs.
