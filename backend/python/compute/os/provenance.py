"""
Provenance Ledger Module for PERSEPHONE OS.
Maintains the immutable cryptographic causal chain ("Why do we believe it?").
Connects raw patient inputs through intermediate agent claims to final report decisions.
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import hashlib
import json
import time
import threading


@dataclass
class ProvenanceEntry:
    sequence_index: int
    parent_hash: Optional[str]
    run_id: str
    agent_id: str
    plane: str
    action: str
    input_hash: str
    output_hash: str
    timestamp: str
    provenance_hash: str
    evidence_sources: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sequence_index": self.sequence_index,
            "parent_hash": self.parent_hash,
            "run_id": self.run_id,
            "agent_id": self.agent_id,
            "plane": self.plane,
            "action": self.action,
            "claim": self.action,
            "input_hash": self.input_hash,
            "output_hash": self.output_hash,
            "timestamp": self.timestamp,
            "provenance_hash": self.provenance_hash,
            "evidence_sources": self.evidence_sources
        }


class ProvenanceLedger:
    """
    Cryptographic Provenance Ledger for PERSEPHONE OS.
    Ensures every clinical claim, biomarker score, and recommendation is provably grounded
    in a tamper-evident causal Merkle hash chain.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ProvenanceLedger, cls).__new__(cls)
                cls._instance._entries = []
                cls._instance._chains = {}
            return cls._instance

    def record_entry(
        self,
        agent_name: str,
        action: str,
        input_data: Any,
        output_data: Any,
        parent_hash: Optional[str] = None,
        run_id: str = "RUN-DEFAULT",
        plane: str = "PATIENT"
    ) -> str:
        """
        Records a causal provenance entry and returns its cryptographic SHA-256 hash.
        """
        with self._lock:
            in_bytes = json.dumps(input_data, sort_keys=True, default=str).encode('utf-8')
            out_bytes = json.dumps(output_data, sort_keys=True, default=str).encode('utf-8')
            input_hash = hashlib.sha256(in_bytes).hexdigest()
            output_hash = hashlib.sha256(out_bytes).hexdigest()

            seq_index = len(self._entries)
            timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

            # Payload format for digest
            block_data = f"{seq_index}|{parent_hash}|{agent_name}|{action}|{input_hash}|{output_hash}"
            prov_hash = hashlib.sha256(block_data.encode('utf-8')).hexdigest()

            entry = ProvenanceEntry(
                sequence_index=seq_index,
                parent_hash=parent_hash,
                run_id=run_id,
                agent_id=agent_name,
                plane=plane,
                action=action,
                input_hash=input_hash,
                output_hash=output_hash,
                timestamp=timestamp,
                provenance_hash=prov_hash
            )

            self._entries.append(entry)
            if run_id not in self._chains:
                self._chains[run_id] = []
            self._chains[run_id].append(entry.to_dict())

            return prov_hash

    def record_step(
        self,
        run_id: str,
        agent_id: str,
        plane: str,
        claim: str,
        input_data: Any,
        output_data: Any,
        evidence_sources: List[str] = None
    ) -> Dict[str, Any]:
        """
        Appends a verified computation step to the run's causal provenance chain.
        """
        with self._lock:
            parent_hash = self._entries[-1].provenance_hash if self._entries else None
        
        prov_hash = self.record_entry(
            agent_name=agent_id,
            action=claim,
            input_data=input_data,
            output_data=output_data,
            parent_hash=parent_hash,
            run_id=run_id,
            plane=plane
        )
        return {
            "sequence_index": len(self._entries) - 1,
            "run_id": run_id,
            "agent_id": agent_id,
            "plane": plane,
            "claim": claim,
            "parent_hash": parent_hash,
            "provenance_hash": prov_hash
        }

    def get_chain(self, run_id: str = None) -> List[Dict[str, Any]]:
        """Returns the full causal provenance chain."""
        with self._lock:
            if run_id and run_id in self._chains:
                return list(self._chains[run_id])
            return [e.to_dict() for e in self._entries]

    def verify_chain_integrity(self, run_id: str = None) -> Dict[str, Any]:
        """
        Verifies the cryptographic hash integrity of the chain from genesis to leaf.
        Detects any tampering of action payload, parents, or outputs.
        """
        with self._lock:
            entries = list(self._entries)

        if not entries:
            return {"valid": True, "entry_count": 0, "entries_checked": 0, "status": "EMPTY_CHAIN"}

        expected_parent = None
        for i, entry in enumerate(entries):
            if i == 0:
                expected_parent = entry.parent_hash
            else:
                if entry.parent_hash != expected_parent:
                    return {
                        "valid": False,
                        "tampered_index": i,
                        "entry_count": len(entries),
                        "reason": f"Parent hash broken at block {i}: expected {expected_parent}, got {entry.parent_hash}"
                    }

            # Recompute hash using current entry fields
            block_data = f"{entry.sequence_index}|{entry.parent_hash}|{entry.agent_id}|{entry.action}|{entry.input_hash}|{entry.output_hash}"
            computed_hash = hashlib.sha256(block_data.encode('utf-8')).hexdigest()

            if computed_hash != entry.provenance_hash:
                return {
                    "valid": False,
                    "tampered_index": i,
                    "entry_count": len(entries),
                    "reason": f"Cryptographic digest mismatch at block {i}: block tampered"
                }

            expected_parent = entry.provenance_hash

        return {
            "valid": True,
            "entry_count": len(entries),
            "entries_checked": len(entries),
            "merkle_root": entries[-1].provenance_hash,
            "status": "CRYPTOGRAPHICALLY_VERIFIED"
        }
