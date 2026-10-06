# Security Policy & Compliance Dossier

## 1. Protected Health Information (PHI) & HIPAA Compliance
PERSEPHONE is an **exploratory computational oncology research prototype and simulation engine**.
- **No Protected Health Information (PHI):** The system does not ingest, store, or transmit identifiable real-world patient records.
- **Synthetic Data Baseline:** All patient profiles (Elena Rostova, Arthur Pendelton, Marcus Vance), synthetic cohorts, IoT telemetry streams, and histopathology/radiology images are entirely **synthetic and simulated** for research and technological benchmarking.
- **Cryptographic Audit Integrity:** Clinical recommendations, decision contexts, and experiment manifests are hashed using SHA-256 and stored in an append-only `ProvenanceLedger` to provide a tamper-evident audit trail without exposing sensitive clinical data.

---

## 2. Research Prototype Disclaimer
> [!WARNING]
> PERSEPHONE is designed exclusively for computational oncology simulation, biomedical modeling, and decision-support research. It is **not approved by the FDA or any global regulatory body for clinical practice, medical diagnosis, or active patient care**. All clinical recommendations, dosing projections, and scenario simulations must be reviewed by board-certified oncologists using validated clinical workflows.

---

## 3. Reporting Vulnerabilities
If you discover a security vulnerability or algorithmic integrity gap in the platform:
1. Do not open a public issue on GitHub.
2. Report the vulnerability privately to the project maintainers at `dev.mehta@persephone-oncology.org`.
3. Please include reproduction steps, environment details, and affected components.
