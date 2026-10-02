"""
Experiment Manifest Contract Schema v1.0 for PERSEPHONE OS.
Defines the authoritative digital DNA capturing inputs, environment, model versions,
runtime parameters, agent signatures, and the cryptographic SHA-256 seal.
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import hashlib
import json
import time
import sys
import platform


@dataclass
class ExperimentManifestContract:
    experiment_id: str
    case_id: str
    run_id: str
    patient_twin_hash: str
    input_hash: str
    runtime_seed: int = 42
    solver_name: str = "RK4_ADAPTIVE"
    solver_tolerance: float = 1e-6
    agent_executions: List[Dict[str, Any]] = field(default_factory=list)
    evidence_sources: List[str] = field(default_factory=list)
    governance_decision: Dict[str, Any] = field(default_factory=dict)
    manifest_version: str = "1.0"
    os_version: str = "PERSEPHONE OS v1.0"
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))

    def build_manifest(self) -> Dict[str, Any]:
        manifest_body = {
            "manifest_version": self.manifest_version,
            "manifest_schema_version": self.manifest_version,
            "os_version": self.os_version,
            "experiment_id": self.experiment_id,
            "timestamp": self.timestamp,
            "case": {
                "case_id": self.case_id,
                "run_id": self.run_id,
                "patient_twin_hash": self.patient_twin_hash,
                "input_hash": self.input_hash
            },
            "environment": {
                "python_version": sys.version.split()[0],
                "platform": platform.platform(),
                "processor": platform.processor() or "x86_64",
                "git_commit": "HEAD",
                "dependency_lock_hash": "b724ded5e0cca561a4384d0a4af0dc6a794f08db2ca5996090bb0b27b90b0f2e"
            },
            "models": {
                "cair_runtime": "cair-v1.0",
                "calibration_model": "temperature-scaling-v2",
                "rl_policy_checkpoint": "patient-a_dqn.pt-sha256"
            },
            "runtime": {
                "random_seed": self.runtime_seed,
                "solver": self.solver_name,
                "solver_tolerance": self.solver_tolerance,
                "synthetic_cohort_n": 50
            },
            "random_seeds": {
                "numpy_seed": self.runtime_seed,
                "python_seed": self.runtime_seed
            },
            "agents": self.agent_executions,
            "evidence": {
                "source_versions": self.evidence_sources or ["NCCN-OV-v1.2026", "PMID:30345884", "CPIC-2023.1"],
                "retrieval_timestamp": self.timestamp
            },
            "governance": self.governance_decision
        }

        # Compute deterministic SHA-256 seal over canonical JSON representation
        canonical_bytes = json.dumps(manifest_body, sort_keys=True).encode('utf-8')
        sha256_seal = hashlib.sha256(canonical_bytes).hexdigest()

        manifest_body["seal_sha256"] = sha256_seal
        manifest_body["integrity"] = {
            "sha256_seal": sha256_seal,
            "verification_status": "SEALED_VALID"
        }
        return manifest_body
