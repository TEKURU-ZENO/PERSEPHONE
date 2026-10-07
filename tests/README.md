# PERSEPHONE Verification & Testing Harness

This directory contains the zero-dependency test coordinator and integration verification suites for the PERSEPHONE platform.

---

## Test Architecture

The testing harness enforces scientific verification and architectural integrity across all 20 phases:

```
tests/
├── simulation/                  # Phase 2: RK4 solver, PK/PD, adaptive therapy
├── graph/                       # Phase 3: Graph pathfinding and mutation-to-drug mappings
├── tumor-board/                 # Phase 4: Deterministic DAG execution and recommendation schema
├── memory/                      # Phase 5: Concept parser, ranking, retrieval, persistence
├── datasets/                    # Phase 6: Ingestion schemas, data quality, normalization
├── integration/                 # Phases 7–20: Python SCR parity, latency, Graph-RAG, RL, CAIR,
│                                #              Multimodal, Genomics, Trials, Monitoring, Response,
│                                #              Counterfactual, Research, Governance, OS Control Plane
├── performance/                 # Subgraph filtering, RK4 speed, Tumor Board latency
└── run-tests.js                 # Central zero-dependency test runner (37 suites)
```

---

## Executing the Test Suites

### 1. End-to-End Integration Suite (Node.js)
Requires Python SCR on port 5000 and Node gateway on port 3000:
```bash
node tests/run-tests.js
```
- **Coverage:** 37 distinct suites verifying all 20 development phases and performance latency targets.
- **Status:** 37 / 37 passing (37/37 suites pass).

### 2. Scientific Unit Tests (Python)
```bash
# Full scientific unit test suite (178 tests)
python -m unittest discover -s backend/python/tests/scientific -v

# Consistency, parity, and registry invariants (12 tests)
python -m unittest backend/python/tests/scientific/test_drug_target_consistency.py -v
```
- **Coverage:** 178 unit tests covering Lotka-Volterra ODEs, RL policies, pharmacogenomics, verified trial matching, and PERSEPHONE OS contracts.
