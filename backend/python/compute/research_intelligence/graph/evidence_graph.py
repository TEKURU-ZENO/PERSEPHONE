"""
Clinical Evidence Graph module for PERSEPHONE Research Intelligence Platform.
Defines a first-class directed knowledge graph connecting Patient, Variants, Pathways,
Drugs, Trials, Publications, Guidelines, Claims, and Agents.
"""
import time
from typing import Dict, List, Optional, Set, Any


class EvidenceNode:
    """
    Represents a typed entity node in the Clinical Evidence Graph.
    """
    VALID_TYPES = {
        "PATIENT", "VARIANT", "BIOMARKER", "PATHWAY",
        "DRUG", "TRIAL", "PUBLICATION", "GUIDELINE", "CLAIM", "AGENT"
    }

    def __init__(self, node_id: str, node_type: str, label: str, properties: Optional[Dict[str, Any]] = None):
        if node_type not in self.VALID_TYPES:
            raise ValueError(f"Invalid EvidenceNode type: {node_type}. Must be one of {self.VALID_TYPES}")
        self.id = node_id
        self.type = node_type
        self.label = label
        self.properties = properties or {}
        self.created_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "label": self.label,
            "properties": self.properties,
            "created_at": self.created_at
        }


class EvidenceEdge:
    """
    Represents a typed directed relationship between two EvidenceNodes.
    """
    VALID_TYPES = {
        "HAS_VARIANT", "ACTIVATES", "TARGETS", "STUDIED_IN",
        "SUPPORTED_BY", "RECOMMENDED_BY", "CONTRADICTS", "GENERATED_BY", "DERIVED_FROM"
    }

    def __init__(self, source_id: str, target_id: str, edge_type: str, properties: Optional[Dict[str, Any]] = None):
        if edge_type not in self.VALID_TYPES:
            raise ValueError(f"Invalid EvidenceEdge type: {edge_type}. Must be one of {self.VALID_TYPES}")
        self.source_id = source_id
        self.target_id = target_id
        self.type = edge_type
        self.properties = properties or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source_id,
            "target": self.target_id,
            "type": self.type,
            "properties": self.properties
        }


class ClinicalEvidenceGraph:
    """
    Authoritative First-Class Graph representation for all clinical evidence,
    scientific literature, trials, guidelines, and claims in PERSEPHONE.
    """
    def __init__(self, graph_id: str = "persephone-evidence-graph"):
        self.graph_id = graph_id
        self.nodes: Dict[str, EvidenceNode] = {}
        self.edges: List[EvidenceEdge] = []
        self._adj_out: Dict[str, List[EvidenceEdge]] = {}
        self._adj_in: Dict[str, List[EvidenceEdge]] = {}

    def add_node(self, node_id: str, node_type: str, label: str, properties: Optional[Dict[str, Any]] = None) -> EvidenceNode:
        if node_id not in self.nodes:
            node = EvidenceNode(node_id, node_type, label, properties)
            self.nodes[node_id] = node
            self._adj_out[node_id] = []
            self._adj_in[node_id] = []
        else:
            node = self.nodes[node_id]
            if properties:
                node.properties.update(properties)
        return node

    def add_edge(self, source_id: str, target_id: str, edge_type: str, properties: Optional[Dict[str, Any]] = None) -> EvidenceEdge:
        if source_id not in self.nodes:
            raise KeyError(f"Source node '{source_id}' does not exist in EvidenceGraph.")
        if target_id not in self.nodes:
            raise KeyError(f"Target node '{target_id}' does not exist in EvidenceGraph.")

        edge = EvidenceEdge(source_id, target_id, edge_type, properties)
        self.edges.append(edge)
        self._adj_out[source_id].append(edge)
        self._adj_in[target_id].append(edge)
        return edge

    def get_node(self, node_id: str) -> Optional[EvidenceNode]:
        return self.nodes.get(node_id)

    def get_outgoing_edges(self, node_id: str, edge_type: Optional[str] = None) -> List[EvidenceEdge]:
        edges = self._adj_out.get(node_id, [])
        if edge_type:
            return [e for e in edges if e.type == edge_type]
        return edges

    def get_incoming_edges(self, node_id: str, edge_type: Optional[str] = None) -> List[EvidenceEdge]:
        edges = self._adj_in.get(node_id, [])
        if edge_type:
            return [e for e in edges if e.type == edge_type]
        return edges

    def get_nodes_by_type(self, node_type: str) -> List[EvidenceNode]:
        return [n for n in self.nodes.values() if n.type == node_type]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "graph_id": self.graph_id,
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [e.to_dict() for e in self.edges]
        }
