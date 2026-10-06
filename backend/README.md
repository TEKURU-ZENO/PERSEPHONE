# PERSEPHONE Backend Architecture

The backend of PERSEPHONE is structured as a decoupled two-tier microservice architecture:

```
┌───────────────────────────────────────┐
│     Client Workstation (Browser)      │
└──────────────────┬────────────────────┘
                   │ HTTP / REST
                   ▼
┌───────────────────────────────────────┐
│  Node.js API Gateway (Port 3000)      │
│  • Static asset streaming             │
│  • Microservice reverse proxy         │
│  • Zero-dependency HTTP server        │
└──────────────────┬────────────────────┘
                   │ Internal Proxy
                   ▼
┌───────────────────────────────────────┐
│  Python Scientific Compute Runtime    │
│  (SCR - Port 5000)                    │
│  • Runge-Kutta 4th-order ODE solver   │
│  • RL Policy Optimization (DQN/AC)    │
│  • COSMIC SBS Mutational Signatures   │
│  • Verified Clinical Trials Matcher   │
│  • 23-Agent Council & OS Kernel       │
└───────────────────────────────────────┘
```

---

## Subsystems

### 1. `backend/node/` (API Gateway)
- **Runtime:** Native Node.js HTTP server (`server.js`).
- **Port:** `3000`.
- **Responsibilities:** Serves dashboard static assets, handles client routing, and transparently proxies scientific API requests (`/api/v1/python/*`) to the Python SCR.

### 2. `backend/python/` (Scientific Compute Runtime — SCR)
- **Runtime:** Python 3.12 (`app.py`), PyTorch (CPU), NumPy, SciPy.
- **Port:** `5000`.
- **Core Modules:**
  - `compute/simulation/`: RK4 numerical ODE solver, Lotka-Volterra equations, PK/PD curves.
  - `compute/optimization/`: RL dosing environment (`OncologyGymEnv`), DQN trainer, Actor-Critic policy inference.
  - `compute/genomics/`: Somatic variant annotator and NNLS mutational signature deconvolution against COSMIC v3.4 SBS matrix.
  - `compute/trials/`: Verified ClinicalTrials.gov matcher with protein change normalization and negative filtering.
  - `compute/os/`: PERSEPHONE OS Kernel, `BlackboardMemory`, `OSEventBus`, `ProvenanceLedger`, `ExperimentManifest`, and `CaseReplayEngine`.
  - `compute/multimodal/`: Diagnostic imaging pipelines flagged explicitly with `is_mock: True`.
  - `tests/scientific/`: 177 unit tests covering all computational models and contracts.
