# Biomedical Knowledge Graph & Graph-RAG v2 Fabric

This directory contains the knowledge graph architecture, relational ontologies, and hybrid retrieval components of PERSEPHONE.

---

## Architecture

### 1. Interactive 2D Canvas Knowledge Graph Explorer (Phase 3)
- **Zero-Dependency Implementation:** Rendered directly on an HTML5 2D Canvas at 60 FPS without external graphing libraries.
- **Physics Engine:** Custom spring-damper layout model simulating Hooke's law on edges and Coulomb electrostatic repulsion on nodes.
- **Pathfinding Algorithm:** Implements depth-first search (DFS) traversal (`GraphService.findCausalPathForPatient`) to isolate patient-specific therapeutic subgraphs:
  $$\text{Patient} \longrightarrow \text{Mutation} \longrightarrow \text{Gene} \longrightarrow \text{Pathway} \longrightarrow \text{Drug} \longrightarrow \text{Clinical Trial}$$

### 2. Graph-RAG v2 Hybrid Reasoning Engine (Phase 8)
- Located under `backend/python/compute/plugins/graph_rag/`.
- **Hybrid Retrieval:** Fuses vector embedding cosine similarity with multi-hop structured graph traversal.
- **Entity Resolution:** Maps genomic variants and clinical terms to standard ontology identifiers (NCBIGene, ClinVar, MeSH).
- **Clinical Grounding Gate:** Strictly validates candidate recommendation claims against verified knowledge edges and literature citations prior to agent presentation.
