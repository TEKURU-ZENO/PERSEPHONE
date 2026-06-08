# Contributing Guidelines

Thank you for contributing to the PERSEPHONE Precision Oncology Platform. To maintain research-grade reproducibility, please adhere to these guidelines.

---

## 1. Branch Naming Conventions
To keep the history of our clinical decision pipeline clean, please name branches according to their target phase:
- `feature/phase-[X]-description` (e.g., `feature/phase-5-graph-rag`)
- `bugfix/issue-description` (e.g., `bugfix/rk4-divergence`)
- `refactor/component-decoupling`

---

## 2. Commit Message Patterns
Commit messages must reflect their architectural impact:
- `feat(sim): add RK4 solver for Lotka-Volterra ecology`
- `fix(store): resolve telemetry state leakage across patient swap`
- `docs(blueprint): update ARCHITECTURE.md schema details`

---

## 3. Pull Request (PR) Workflow
1. Branch off the `main` development line.
2. Code your components ensuring that all simulation variables are linked to the Parameter Registry.
3. Add unit test suites under `tests/` validating your mathematical solver or graph path calculations.
4. Open a PR mapping out the factual vs counterfactual delta verifications.

---

## 4. Coding Standards

### ES Modules constraint
- All JavaScript files must be written as **ES Modules** using standard `import`/`export` syntax.
- File extensions (`.js`, `.json`) are **mandatory** in all relative import paths (e.g. `import { GraphService } from './graph.service.js';`).

### Zero-Dependency Constraint
- The core workstation, server, and testing suites must remain **zero-dependency**. No packages should be added to `package.json` for compilation, state, routing, or assertions.
- Rely strictly on native browser APIs and Node's built-in modules (`fs`, `path`, `http`, `assert`).

### Mathematical Integrity Rules
- Every numerical solver must enforce physical boundary constraints: cell counts, toxicity, and drug concentrations cannot drop below zero (`Math.max(0, val)`).
- Growth rates must adhere to resistance fitness costs: resistant clones must proliferate slower than sensitive clones in the absence of treatment ($\alpha_2 < \alpha_1$).
