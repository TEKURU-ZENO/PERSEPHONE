# ADR-003: Zero-Dependency HTML5 Canvas Knowledge Graph Explorer

## Status
Accepted

## Context
Precision oncology requires mapping high-dimensional connections between patients, genetic variants, target genes, biological pathways, therapeutic agents, clinical trials, and toxicological side effects. We need a visualization component that handles this relational network interactively, maintaining smooth rendering speeds without massive bundle footprints.

## Decision
We implemented a custom, **zero-dependency HTML5 Canvas 2D force-directed layout engine**:
- **Rendering Model:** Draws nodes and edges directly on a canvas coordinate space, avoiding DOM overhead.
- **Physics Solver:** Implements spring-damper attractive forces for edges and electrostatic repulsive forces for nodes.
- **Pathfinding Algorithm:** Uses a depth-first traversal utility (`GraphService.findCausalPathForPatient`) to isolate the target subgraphs for specific patients (e.g. BRCA1 for Elena, EGFR for Arthur).

## Consequences
- **Advantages:** Zero external packages (no D3, no cytoscape.js), exceptional performance (constant 60 FPS), and instant path tracing.
- **Disadvantages:** Graph modifications must be done via Javascript state arrays rather than standard query languages (like Cypher), which will be addressed in Phase 5 Graph-RAG.
