"""
Evidence Graph Traverser module for PERSEPHONE Research Intelligence Platform.
Performs topological traversals, lineage backtracing, and subgraph extraction.
"""
from typing import Dict, List, Set, Any
from backend.python.compute.research_intelligence.graph.evidence_graph import ClinicalEvidenceGraph, EvidenceNode


class EvidenceGraphTraverser:
    """
    Utility for querying and extracting lineage subgraphs from a ClinicalEvidenceGraph.
    """

    @classmethod
    def trace_claim_lineage(cls, graph: ClinicalEvidenceGraph, claim_id: str) -> Dict[str, Any]:
        """
        Backtraces a clinical claim through Evidence, Trials/Publications, Drugs, Pathways, and Variants.
        """
        claim_node = graph.get_node(claim_id)
        if not claim_node:
            return {"error": f"Claim node '{claim_id}' not found in graph."}

        visited_nodes: Set[str] = set()
        subgraph_nodes: List[Dict[str, Any]] = []
        subgraph_edges: List[Dict[str, Any]] = []

        def dfs_backward(curr_id: str):
            if curr_id in visited_nodes:
                return
            visited_nodes.add(curr_id)
            node = graph.get_node(curr_id)
            if node:
                subgraph_nodes.append(node.to_dict())

            # Follow incoming edges (evidence -> claim, publication -> evidence, etc.)
            for edge in graph.get_incoming_edges(curr_id):
                subgraph_edges.append(edge.to_dict())
                dfs_backward(edge.source_id)

        dfs_backward(claim_id)

        return {
            "root_claim_id": claim_id,
            "nodes": subgraph_nodes,
            "edges": subgraph_edges,
            "node_count": len(subgraph_nodes),
            "edge_count": len(subgraph_edges)
        }

    @classmethod
    def trace_patient_evidence_tree(cls, graph: ClinicalEvidenceGraph, patient_id: str) -> Dict[str, Any]:
        """
        Forward-traces the complete evidence chain originating from an index patient:
        Patient -> Variants -> Pathways -> Drugs -> Trials -> Publications -> Guidelines -> Claims
        """
        patient_node = graph.get_node(patient_id)
        if not patient_node:
            return {"error": f"Patient node '{patient_id}' not found in graph."}

        visited: Set[str] = set()
        subgraph_nodes: List[Dict[str, Any]] = []
        subgraph_edges: List[Dict[str, Any]] = []

        def dfs_forward(curr_id: str):
            if curr_id in visited:
                return
            visited.add(curr_id)
            node = graph.get_node(curr_id)
            if node:
                subgraph_nodes.append(node.to_dict())

            for edge in graph.get_outgoing_edges(curr_id):
                subgraph_edges.append(edge.to_dict())
                dfs_forward(edge.target_id)

        dfs_forward(patient_id)

        return {
            "root_patient_id": patient_id,
            "nodes": subgraph_nodes,
            "edges": subgraph_edges,
            "depth": len(visited)
        }
