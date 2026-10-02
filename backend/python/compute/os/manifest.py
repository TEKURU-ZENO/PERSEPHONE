"""
Experiment Manifest Engine for PERSEPHONE OS.
Assembles and verifies Schema v1.0 manifests capturing complete case DNA
and sealing them with SHA-256 digests.
"""
from typing import Dict, List, Any
import hashlib
import json
from backend.python.compute.os.contracts.manifest import ExperimentManifestContract
from backend.python.compute.os.context import ClinicalCaseContext


class ExperimentManifestEngine:
    """
    Constructs and verifies immutable Experiment Manifests.
    """

    @classmethod
    def generate_manifest(
        cls,
        context: ClinicalCaseContext,
        agent_executions: List[Dict[str, Any]] = None,
        runtime_seed: int = 42
    ) -> Dict[str, Any]:
        """
        Builds a Schema v1.0 manifest for the given case context and seals it.
        """
        pt_bytes = json.dumps(context.patient_twin, sort_keys=True, default=str).encode('utf-8')
        in_bytes = json.dumps(context.inputs, sort_keys=True, default=str).encode('utf-8')

        pt_hash = hashlib.sha256(pt_bytes).hexdigest()
        in_hash = hashlib.sha256(in_bytes).hexdigest()

        contract = ExperimentManifestContract(
            experiment_id=f"EXP-{context.case_id.upper()}-{context.run_id}",
            case_id=context.case_id,
            run_id=context.run_id,
            patient_twin_hash=pt_hash,
            input_hash=in_hash,
            runtime_seed=runtime_seed,
            agent_executions=agent_executions or [],
            evidence_sources=["NCCN-OV-v1.2026", "PMID:30345884", "CPIC-2023.1", "CTCAE-v5.0", "KDIGO-2024"],
            governance_decision=context.governance_state or {"decision_status": "SUPPORTED"}
        )

        return contract.build_manifest()

    @classmethod
    def create_manifest(
        cls,
        context: ClinicalCaseContext,
        seed: int = 42,
        agent_executions: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Convenience alias for generate_manifest."""
        return cls.generate_manifest(context, agent_executions=agent_executions, runtime_seed=seed)

    @classmethod
    def verify_manifest(cls, manifest_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates the cryptographic integrity of a manifest against its SHA-256 seal.
        Detects any tampering in inputs, model versions, runtime parameters, or governance decisions.
        """
        original_seal = (
            manifest_data.get("seal_sha256") or
            manifest_data.get("integrity", {}).get("sha256_seal")
        )
        if not original_seal:
            return {
                "valid": False,
                "reason": "Missing integrity seal in manifest"
            }

        # Reconstruct canonical payload without seal keys
        unsealed = dict(manifest_data)
        unsealed.pop("integrity", None)
        unsealed.pop("seal_sha256", None)

        canonical_bytes = json.dumps(unsealed, sort_keys=True).encode('utf-8')
        computed_seal = hashlib.sha256(canonical_bytes).hexdigest()

        is_valid = (computed_seal == original_seal)

        return {
            "valid": is_valid,
            "original_seal": original_seal,
            "computed_seal": computed_seal,
            "status": "SEAL_VERIFIED" if is_valid else "TAMPERING_DETECTED",
            "experiment_id": manifest_data.get("experiment_id")
        }

    @classmethod
    def verify_manifest_seal(cls, manifest_data: Dict[str, Any]) -> bool:
        """Boolean check for manifest seal integrity."""
        return cls.verify_manifest(manifest_data)["valid"]
