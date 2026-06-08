# ADR-001: Deterministic Directed Acyclic Graph (DAG) for Agentic Orchestration

## Status
Accepted

## Context
Precision oncology decision support requires high explainability, scientific safety, and reproducibility. Traditional generative AI agents with autonomous, non-deterministic loops can hallucinate clinical recommendations or run into cyclic reasoning. We need a robust architecture to coordinate the 5 specialized oncology agents (Evolution, Planning, Evidence, Safety, Consensus) while ensuring a reviewable audit trail.

## Decision
We chose to implement a stateful, deterministic **Directed Acyclic Graph (DAG)** orchestration pipeline running in JavaScript.
- Each agent step is a node in the DAG.
- Data flows sequentially: `Evolution` $\to$ `Planning` $\to$ `Evidence` & `Safety` (parallel/sequential evaluation) $\to$ `Clinical Consensus`.
- The outputs of preceding agents are appended to the pipeline context and made available to subsequent nodes.
- Execution steps are logged sequentially with typing/typewriter animations to the user interface.

## Consequences
- **Advantages:** Guaranteed termination, 100% reproducible execution paths, and clean audit trails (`audit/recommendations/`).
- **Disadvantages:** Less flexibility in dynamic tool use; however, this is a necessary tradeoff in medical/clinical settings where safety is paramount.
