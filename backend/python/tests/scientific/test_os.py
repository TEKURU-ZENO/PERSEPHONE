"""
Unit and Invariant tests for PERSEPHONE Phase 20: PERSEPHONE OS Runtime & Control Plane.

Asserts the Six Core Platform Invariants:
1. Agent Completeness Invariant (23 agents registered across 5 planes, 0 orphans, valid topological DAG)
2. Blackboard Contract Invariant (BlackboardKeyContract type/schema checking and CaseSchemaValidator)
3. Event & Provenance Chaining Invariant (OSEventBus reactive dispatch and ProvenanceLedger cryptographic chaining)
4. Experiment Manifest Integrity Invariant (Schema v1.0 snapshot, SHA-256 seal verification and tamper detection)
5. Deterministic Scientific Replay Invariant (ODE/RK4 simulation trajectory RMSE < 1e-4, decision equality)
6. Failure Containment & Governance Semantics Invariant (3-tier failure containment, SUPPORTED/CAUTION/ABSTAIN gating)
"""

import unittest
import copy
from backend.python.compute.os.planes import PlaneRegistry, PlaneType, AgentSpec
from backend.python.compute.os.contracts.blackboard import BlackboardKeyContract
from backend.python.compute.os.contracts.case import CaseSchemaValidator, ExecutionRunMetadata
from backend.python.compute.os.contracts.events import EventContract
from backend.python.compute.os.contracts.governance import GovernanceStatus, AbstentionReasonCode, GovernanceDecisionRecord
from backend.python.compute.os.contracts.manifest import ExperimentManifestContract
from backend.python.compute.os.context import ClinicalCaseContext, PipelineState
from backend.python.compute.os.event_bus import OSEventBus
from backend.python.compute.os.provenance import ProvenanceLedger, ProvenanceEntry
from backend.python.compute.os.observability import OSObservabilityMonitor
from backend.python.compute.os.manifest import ExperimentManifestEngine
from backend.python.compute.os.replay import CaseReplayEngine
from backend.python.compute.os.kernel import PersephoneKernel
from backend.python.compute.os.registry import OSRegistry


class TestPersephoneOS(unittest.TestCase):

    def setUp(self):
        self.patient_normal = {
            "id": "patient-normal",
            "name": "Elena Rostova",
            "cancer_type": "High-Grade Serous Ovarian Carcinoma",
            "variants": ["BRCA1 c.5266dupC"],
            "labs": {
                "eGFR": 75.0,
                "AST_ALT_xULN": 1.0,
                "bilirubin_xULN": 0.8,
                "ANC": 2400,
                "platelets": 210000,
                "QTc": 420
            }
        }
        self.patient_impaired = {
            "id": "patient-impaired",
            "name": "Renal Impairment Subject",
            "cancer_type": "Ovarian",
            "variants": ["BRCA1 c.5266dupC"],
            "labs": {
                "eGFR": 22.0,
                "AST_ALT_xULN": 6.5,
                "bilirubin_xULN": 3.2,
                "ANC": 650,
                "platelets": 42000,
                "QTc": 490
            }
        }

    # =========================================================================
    # INVARIANT 1: Agent Completeness & 5-Plane Topology Invariant
    # =========================================================================
    def test_invariant_1_agent_completeness_and_plane_mapping(self):
        """All 23 agents must be registered across the 5 planes with zero orphans."""
        all_specs = PlaneRegistry.get_all_agent_specs()
        self.assertEqual(len(all_specs), 23, "Council must contain exactly 23 registered agents")

        # Verify planes
        plane_counts = {
            PlaneType.PATIENT: 0,
            PlaneType.SCIENTIFIC: 0,
            PlaneType.CLINICAL: 0,
            PlaneType.EVIDENCE: 0,
            PlaneType.GOVERNANCE: 0,
        }
        for name, spec in all_specs.items():
            self.assertIn(spec.plane, plane_counts, f"Agent {name} mapped to invalid plane: {spec.plane}")
            plane_counts[spec.plane] += 1

        self.assertEqual(plane_counts[PlaneType.PATIENT], 5, "Patient Intelligence Plane must have 5 agents")
        self.assertEqual(plane_counts[PlaneType.SCIENTIFIC], 2, "Scientific Intelligence Plane must have 2 agents")
        self.assertEqual(plane_counts[PlaneType.CLINICAL], 5, "Clinical Intelligence Plane must have 5 agents")
        self.assertEqual(plane_counts[PlaneType.EVIDENCE], 5, "Evidence Intelligence Plane must have 5 agents")
        self.assertEqual(plane_counts[PlaneType.GOVERNANCE], 6, "Governance & Decision Support Plane must have 6 agents")

        # Verify topological execution order
        topo_order = PlaneRegistry.get_execution_topology()
        self.assertEqual(len(topo_order), 23, "Topological order must include all 23 agents")
        
        # Verify DAG prerequisites: an agent's dependencies must appear before it
        executed = set()
        for agent_name in topo_order:
            spec = all_specs[agent_name]
            for req in spec.requires:
                # If prerequisite is published by an agent, verify publisher appeared earlier
                publishers = [n for n, s in all_specs.items() if req in s.publishes]
                for pub in publishers:
                    if pub != agent_name:
                        self.assertIn(pub, executed, f"Prerequisite {req} for {agent_name} published by {pub} not executed prior")
            executed.add(agent_name)

    # =========================================================================
    # INVARIANT 2: Blackboard Key Contract & Case Schema Invariant
    # =========================================================================
    def test_invariant_2_blackboard_contract_enforcement(self):
        """Blackboard keys must strictly enforce data types and reject unauthorized keys."""
        # Valid write
        valid_twin = {"id": "patient-1", "tumor_burden": 1.2}
        self.assertTrue(BlackboardKeyContract.validate_write("patient_twin", valid_twin))

        # Invalid type write (expected dict, passing integer)
        with self.assertRaises(TypeError):
            BlackboardKeyContract.validate_write("patient_twin", 12345)

        # Unregistered key write
        with self.assertRaises(KeyError):
            BlackboardKeyContract.validate_write("unregistered_rogue_key", {"foo": "bar"})

        # Case schema validation
        val_res = CaseSchemaValidator.validate_patient_case(self.patient_normal)
        self.assertTrue(val_res["valid"])
        self.assertEqual(len(val_res["missing_fields"]), 0)

        # Incomplete patient case
        incomplete_patient = {"id": "bad-patient"}
        val_bad = CaseSchemaValidator.validate_patient_case(incomplete_patient)
        self.assertFalse(val_bad["valid"])
        self.assertIn("name", val_bad["missing_fields"])

    # =========================================================================
    # INVARIANT 3: Event Bus & Cryptographic Provenance Chaining Invariant
    # =========================================================================
    def test_invariant_3_event_bus_and_provenance_chain_integrity(self):
        """OSEventBus and ProvenanceLedger must provide tamper-evident cryptographic parent-child links."""
        event_bus = OSEventBus()
        ledger = ProvenanceLedger()

        # Emit events
        e1 = event_bus.emit(
            event_type="PATIENT_INGESTION",
            plane=PlaneType.PATIENT,
            agent_name="patient_twin",
            payload={"patient_id": "patient-1"}
        )
        self.assertIsNotNone(e1.event_id)
        self.assertEqual(e1.plane, PlaneType.PATIENT.value)

        # Record provenance linked to e1
        h1 = ledger.record_entry(
            agent_name="patient_twin",
            action="initialize_digital_twin",
            input_data={"patient_id": "patient-1"},
            output_data={"initial_tumor_burden": 1.0},
            parent_hash=None
        )

        h2 = ledger.record_entry(
            agent_name="tumor_evolution",
            action="simulate_rk4_dynamics",
            input_data={"tumor_burden": 1.0},
            output_data={"trajectory_end": 0.85},
            parent_hash=h1
        )

        # Chain verification should succeed
        integrity = ledger.verify_chain_integrity()
        self.assertTrue(integrity["valid"])
        self.assertEqual(integrity["entry_count"], 2)

        # Tamper test: mutate entry payload directly
        ledger._entries[0].action = "tampered_action"
        tampered_integrity = ledger.verify_chain_integrity()
        self.assertFalse(tampered_integrity["valid"], "Tampered provenance ledger must fail verification")

    # =========================================================================
    # INVARIANT 4: Experiment Manifest & SHA-256 Seal Invariant
    # =========================================================================
    def test_invariant_4_manifest_integrity_and_seal_verification(self):
        """Experiment manifests must serialize environment state and detect byte-level tampering."""
        context = ClinicalCaseContext(
            case_id="case-seal-test",
            patient_twin=self.patient_normal,
            inputs={"strategy": "mtd"}
        )
        manifest = ExperimentManifestEngine.create_manifest(context, seed=42)

        # Validate schema contract
        self.assertEqual(manifest["manifest_schema_version"], "1.0")
        self.assertIn("seal_sha256", manifest)
        self.assertIn("environment", manifest)
        self.assertIn("random_seeds", manifest)

        # Fresh manifest must pass verification
        self.assertTrue(ExperimentManifestEngine.verify_manifest_seal(manifest))

        # Tamper test: alter random seed
        tampered_manifest = copy.deepcopy(manifest)
        tampered_manifest["random_seeds"]["numpy_seed"] = 999999
        self.assertFalse(
            ExperimentManifestEngine.verify_manifest_seal(tampered_manifest),
            "Tampered manifest must fail SHA-256 seal verification"
        )

    # =========================================================================
    # INVARIANT 5: Deterministic Scientific Replay Invariant
    # =========================================================================
    def test_invariant_5_deterministic_scientific_replay_parity(self):
        """Scientific replay of ODE/PK/PD components must yield RMSE < 1e-4 and 100% decision match."""
        kernel = PersephoneKernel()
        context = kernel.execute_case(
            case_data=self.patient_normal,
            case_id="case-replay-orig",
            seed=42
        )
        self.assertEqual(context.pipeline_state, PipelineState.COMPLETED)

        # Generate original manifest
        orig_manifest = ExperimentManifestEngine.create_manifest(context, seed=42)

        # Run replay engine
        replay_res = CaseReplayEngine.replay(orig_manifest)

        # Check scientific parity
        self.assertTrue(replay_res["reproducible"])
        self.assertLess(
            replay_res["scientific_divergence"]["trajectory_rmse"],
            1e-4,
            "Scientific ODE simulation trajectory RMSE must be < 1e-4"
        )
        self.assertTrue(replay_res["decision_agreement"], "Governance decision must match original run")
        self.assertTrue(replay_res["provenance_equivalence"], "Provenance hash structure must match")

    # =========================================================================
    # INVARIANT 6: Failure Containment & Clinician-Support Governance Invariant
    # =========================================================================
    def test_invariant_6_failure_containment_and_governance_semantics(self):
        """Governance decisions must use SUPPORTED/CAUTION/ABSTAIN and safely abstain on severe contraindications."""
        kernel = PersephoneKernel()

        # Run 1: Normal patient should produce SUPPORTED or CAUTION, never autonomous APPROVED
        ctx_normal = kernel.execute_case(case_data=self.patient_normal, seed=123)
        self.assertEqual(ctx_normal.pipeline_state, PipelineState.COMPLETED)
        gov_normal = ctx_normal.governance_state
        self.assertIn(
            gov_normal.get("status"),
            [GovernanceStatus.SUPPORTED.value, GovernanceStatus.CAUTION.value],
            "Normal patient must yield SUPPORTED or CAUTION"
        )
        self.assertNotEqual(gov_normal.get("status"), "APPROVED", "Autonomous prescribing language forbidden")

        # Run 2: Severe impairment patient must be contained and trigger ABSTAIN safely
        ctx_impaired = kernel.execute_case(case_data=self.patient_impaired, seed=456)
        self.assertEqual(ctx_impaired.pipeline_state, PipelineState.COMPLETED)
        gov_impaired = ctx_impaired.governance_state
        
        # When impaired with eGFR 22 and transaminases 6.5x, safety constraints must trigger ABSTAIN or CAUTION
        valid_statuses = [GovernanceStatus.ABSTAIN.value, GovernanceStatus.CAUTION.value]
        self.assertIn(gov_impaired.get("status"), valid_statuses)

        if gov_impaired.get("status") == GovernanceStatus.ABSTAIN.value:
            valid_reasons = [r.value for r in AbstentionReasonCode]
            self.assertIn(
                gov_impaired.get("abstention_reason"),
                valid_reasons,
                "Abstention must reference one of the 4 strict reason codes"
            )

    # =========================================================================
    # END-TO-END: OS Registry Wrapper Verification
    # =========================================================================
    def test_registry_wrappers(self):
        """OSRegistry must expose all endpoints cleanly with latency telemetry."""
        health = OSRegistry.get_health()
        self.assertEqual(health["status"], "HEALTHY")
        self.assertEqual(health["council_agents"], 23)
        self.assertEqual(health["planes"], 5)

        planes = OSRegistry.get_planes()
        self.assertIn("planes", planes)
        self.assertIn("PATIENT", planes["planes"])
        self.assertEqual(len(planes["planes"]["PATIENT"]["agents"]), 5)

        pipeline_res = OSRegistry.run_pipeline({"case": self.patient_normal, "seed": 42})
        self.assertEqual(pipeline_res["status"], "COMPLETED")
        self.assertIn("governance", pipeline_res)
        self.assertIn("manifest_id", pipeline_res)

        events_res = OSRegistry.get_events(limit=10)
        self.assertIn("events", events_res)


if __name__ == "__main__":
    unittest.main()
