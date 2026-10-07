# 23-Agent Collaborative Council & Orchestration Fabric

This directory coordinates the rule-based decision pipeline architecture for the PERSEPHONE Precision Oncology Platform.

---

## 1. Council Structure Across 5 Intelligence Planes

PERSEPHONE orchestrates 23 specialized rule-based oncology agents organized across five operational intelligence planes:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          23-AGENT COLLABORATIVE COUNCIL                     │
├──────────────────────────┬──────────────────────────┬───────────────────────┤
│ Patient Plane            │ Scientific Plane         │ Clinical Plane        │
│ • EvolutionAgent         │ • TherapyPlannerAgent    │ • PharmacologyAgent   │
│ • MonitoringAgent        │ • EpistemicAgent         │ • GenomicsAgent       │
│ • PathologyAgent         │ • CounterfactualAgent    │ • ResistanceAgent     │
│ • RadiologyAgent         │                          │ • ToxicityAgent       │
│ • MolecularAgent         │                          │ • BiomarkerAgent      │
│                          │                          │ • MultiOmicsAgent     │
├──────────────────────────┴──────────────────────────┴───────────────────────┤
│ Evidence Plane                                      │ Governance Plane      │
│ • EvidenceAgent                                     │ • SafetyAgent         │
│ • TrialsAgent                                       │ • GuidelineAgent      │
│ • ProtocolAgent                                     │ • GovernanceAgent     │
│ • ResearchIntelligenceAgent                         │ • ConsensusAgent      │
└─────────────────────────────────────────────────────┴───────────────────────┘
```

---

## 2. Deterministic DAG Execution Pipeline

In the client dashboard, the primary deliberative council executes a deterministic Directed Acyclic Graph (DAG):
1. **`EVOLUTION`**: Evaluates clonal growth rates, progression hazards, and TTP trajectories.
2. **`PLANNING`**: Schedules regimen strategies, comparing standard MTD against rule-based adaptive holds.
3. **`EVIDENCE`**: Crawls verified ClinicalTrials.gov protocols and literature citations.
4. **`SAFETY`**: Evaluates organ-clearance safety rules and toxicity accumulations.
5. **`CONSENSUS`**: Synthesizes inputs into a 0–100 Evidence Strength Score and formal clinical recommendation.

---

## 3. Zero-External-LLM Guarantee
To maintain clinical safety, deterministic reproducibility, and audit readiness, all 23 agents operate via deterministic algorithmic rule engines, mathematical models, and structured ontologies without non-deterministic external LLMs.
