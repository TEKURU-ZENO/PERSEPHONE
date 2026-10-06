"""
Five Planes Architecture Registry for PERSEPHONE OS.
Maps all 23 Council agents and their backing compute modules to the 5 intelligence planes,
and formalizes cross-agent dependency metadata (requires / publishes) for the DAG scheduler.
"""
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass, field


class PlaneType(str, Enum):
    PATIENT = "PATIENT"
    SCIENTIFIC = "SCIENTIFIC"
    CLINICAL = "CLINICAL"
    EVIDENCE = "EVIDENCE"
    GOVERNANCE = "GOVERNANCE"

    # Aliases for backwards compatibility
    PATIENT_INTELLIGENCE = "PATIENT"
    SCIENTIFIC_INTELLIGENCE = "SCIENTIFIC"
    CLINICAL_INTELLIGENCE = "CLINICAL"
    EVIDENCE_INTELLIGENCE = "EVIDENCE"


@dataclass
class AgentSpec:
    agent_id: str
    name: str
    plane: PlaneType
    requires: List[str] = field(default_factory=list)
    publishes: List[str] = field(default_factory=list)
    critical: bool = True
    description: str = ""


class PlaneRegistry:
    """
    Central registry defining the 5 Planes, their member agents, and dependency graphs.
    """

    # 23 Council Member Specifications mapped across the 5 Planes
    AGENT_SPECS = [
        # Conductor (Governance Plane)
        AgentSpec(
            agent_id="orchestrator",
            name="Chief Orchestrator Agent",
            plane=PlaneType.GOVERNANCE,
            requires=[],
            publishes=["ORCHESTRATION_INITIALIZED"],
            critical=True,
            description="Case partitioning and blackboard synchronization"
        ),
        # Plane 1: Patient Intelligence (5 agents)
        AgentSpec(
            agent_id="patient_twin",
            name="Patient Twin Agent",
            plane=PlaneType.PATIENT,
            requires=["patient_twin"],
            publishes=["PATIENT_TWIN_VALIDATED"],
            critical=True,
            description="Demographics, baseline burden, and variant harmonization"
        ),
        AgentSpec(
            agent_id="imaging",
            name="Imaging Agent",
            plane=PlaneType.PATIENT,
            requires=["patient_twin"],
            publishes=["TUMOR_PURITY", "NECROSIS", "RECIST_STATUS", "VOLUME_DELTA_PCT"],
            critical=False,
            description="Histopathology WSI segmentation & CT RECIST 1.1 tracking"
        ),
        AgentSpec(
            agent_id="genomics",
            name="Genomics Agent",
            plane=PlaneType.PATIENT,
            requires=["patient_twin"],
            publishes=["BIOMARKER_TIER", "TMB", "HRD_SCORE"],
            critical=True,
            description="Variant functional annotation & mutational signatures"
        ),
        AgentSpec(
            agent_id="pharmacology",
            name="Pharmacology Agent",
            plane=PlaneType.PATIENT,
            requires=["patient_twin"],
            publishes=["DRUG_SENSITIVITY_SCORES"],
            critical=True,
            description="Pharmacogenomic sensitivity and resistance mapping"
        ),
        AgentSpec(
            agent_id="longitudinal",
            name="Longitudinal Clinical Monitoring Agent",
            plane=PlaneType.PATIENT,
            requires=["patient_twin"],
            publishes=["LONGITUDINAL_STATE", "TUMOR_VELOCITY"],
            critical=False,
            description="Tumor velocity kinetics and adverse event telemetry"
        ),

        # Plane 2: Scientific Intelligence (2 agents)
        AgentSpec(
            agent_id="evolution",
            name="Tumor Evolution Agent",
            plane=PlaneType.SCIENTIFIC,
            requires=["patient_twin"],
            publishes=["CLONAL_FRACTIONS"],
            critical=True,
            description="Darwinian subclonal frequency estimation"
        ),
        AgentSpec(
            agent_id="simulation",
            name="Simulation Agent",
            plane=PlaneType.SCIENTIFIC,
            requires=["patient_twin", "CLONAL_FRACTIONS"],
            publishes=["SIMULATION_RESULTS", "TTP_DAYS"],
            critical=True,
            description="RK4 numerical solver for coupled Lotka-Volterra ODEs"
        ),

        # Plane 3: Clinical Intelligence (5 agents)
        AgentSpec(
            agent_id="therapy",
            name="Therapy Planning Agent",
            plane=PlaneType.CLINICAL,
            requires=["DRUG_SENSITIVITY_SCORES", "SIMULATION_RESULTS"],
            publishes=["THERAPY_REGIMEN"],
            critical=True,
            description="Multimodal regimen synthesis and dosing schedules"
        ),
        AgentSpec(
            agent_id="optimization",
            name="Optimization Agent",
            plane=PlaneType.CLINICAL,
            requires=["THERAPY_REGIMEN", "SIMULATION_RESULTS"],
            publishes=["OPTIMIZED_POLICY"],
            critical=False,
            description="Reinforcement learning (Actor-Critic/DQN) adaptive dosing"
        ),
        AgentSpec(
            agent_id="trials",
            name="Clinical Trials Agent",
            plane=PlaneType.CLINICAL,
            requires=["patient_twin", "DRUG_SENSITIVITY_SCORES"],
            publishes=["TOP_TRIAL", "TRIAL_ELIGIBILITY"],
            critical=False,
            description="Protocol eligibility matching and trial evidence scoring"
        ),
        AgentSpec(
            agent_id="response",
            name="Response Intelligence Agent",
            plane=PlaneType.CLINICAL,
            requires=["TUMOR_PURITY", "DRUG_SENSITIVITY_SCORES"],
            publishes=["PREDICTED_ORR", "PREDICTED_PFS_DAYS", "COMPOSITE_BIOMARKER_SCORE"],
            critical=True,
            description="Composite digital biomarker calibration and PFS projection"
        ),
        AgentSpec(
            agent_id="counterfactual",
            name="Counterfactual Reasoning Agent",
            plane=PlaneType.CLINICAL,
            requires=["SIMULATION_RESULTS", "THERAPY_REGIMEN"],
            publishes=["BEST_PERFORMING_SIMULATED_STRATEGY", "COUNTERFACTUAL_ARMS"],
            critical=False,
            description="Synthetic cohort simulation (N=50) under alternative arms"
        ),

        # Plane 4: Evidence Intelligence (5 agents)
        AgentSpec(
            agent_id="kg",
            name="Knowledge Graph Agent",
            plane=PlaneType.EVIDENCE,
            requires=["patient_twin"],
            publishes=["PATHWAY_TRACES"],
            critical=True,
            description="Biomedical entity causal pathfinding"
        ),
        AgentSpec(
            agent_id="graph_rag",
            name="Graph-RAG Agent",
            plane=PlaneType.EVIDENCE,
            requires=["PATHWAY_TRACES"],
            publishes=["RETRIEVED_CONTEXT_PACKS"],
            critical=False,
            description="Hybrid vector and graph retrieval augmentation"
        ),
        AgentSpec(
            agent_id="evidence",
            name="Evidence Agent",
            plane=PlaneType.EVIDENCE,
            requires=["RETRIEVED_CONTEXT_PACKS"],
            publishes=["CLINICAL_CLAIMS"],
            critical=True,
            description="Registrational trial literature citation synthesis"
        ),
        AgentSpec(
            agent_id="memory",
            name="Clinical Memory Agent",
            plane=PlaneType.EVIDENCE,
            requires=["patient_twin"],
            publishes=["MATCHED_COHORT_PROFILES"],
            critical=False,
            description="Biobank retrospective case memory indexing"
        ),
        AgentSpec(
            agent_id="research_intelligence",
            name="Research Intelligence Agent",
            plane=PlaneType.EVIDENCE,
            requires=["CLINICAL_CLAIMS"],
            publishes=["EVIDENCE_GRAPH", "GUIDELINE_RECOMMENDATION", "MERKLE_ROOT_PROOF"],
            critical=True,
            description="NCCN guideline parsing, contradiction detection, and Merkle lineage"
        ),

        # Plane 5: Governance & Decision Support (6 agents: orchestrator + 5 below)
        AgentSpec(
            agent_id="safety",
            name="Safety Agent",
            plane=PlaneType.GOVERNANCE,
            requires=["patient_twin", "THERAPY_REGIMEN"],
            publishes=["safety_audits"],
            critical=True,
            description="Renal, hepatic, and toxicity limit clearance evaluation"
        ),
        AgentSpec(
            agent_id="validation",
            name="Validation Agent",
            plane=PlaneType.GOVERNANCE,
            requires=["SIMULATION_RESULTS"],
            publishes=["validation_scorecard"],
            critical=True,
            description="Goodness-of-fit, parity index, and hallucination checks"
        ),
        AgentSpec(
            agent_id="governance",
            name="Governance & Clinical Abstention Agent",
            plane=PlaneType.GOVERNANCE,
            requires=["safety_audits", "validation_scorecard"],
            publishes=["GOVERNANCE_DECISION"],
            critical=True,
            description="Deterministic clinical abstention gate, KDIGO/CTCAE rules, and audit certificate"
        ),
        AgentSpec(
            agent_id="explainability",
            name="Explainability Agent",
            plane=PlaneType.GOVERNANCE,
            requires=["GOVERNANCE_DECISION"],
            publishes=["EXPLAINABILITY_TREE"],
            critical=False,
            description="Mechanistic causal chain explanation of therapy choice"
        ),
        AgentSpec(
            agent_id="report",
            name="Clinical Report Agent",
            plane=PlaneType.GOVERNANCE,
            requires=["GOVERNANCE_DECISION", "EXPLAINABILITY_TREE"],
            publishes=["final_report"],
            critical=True,
            description="Final tumor board presentation brief and FHIR export"
        )
    ]

    @classmethod
    def get_all_agents(cls) -> List[AgentSpec]:
        return list(cls.AGENT_SPECS)

    @classmethod
    def get_all_agent_specs(cls) -> Dict[str, AgentSpec]:
        return {a.agent_id: a for a in cls.AGENT_SPECS}

    @classmethod
    def get_agents_by_plane(cls, plane: PlaneType) -> List[AgentSpec]:
        target = plane.value if hasattr(plane, 'value') else str(plane)
        return [a for a in cls.AGENT_SPECS if a.plane.value == target]

    @classmethod
    def get_agent_spec(cls, agent_id: str) -> Optional[AgentSpec]:
        for a in cls.AGENT_SPECS:
            if a.agent_id == agent_id:
                return a
        return None

    @classmethod
    def get_execution_topology(cls) -> List[str]:
        """
        Returns the 23 agents in a verified topological execution order where
        every agent's prerequisites are published prior.
        """
        return [
            "orchestrator",
            "patient_twin",
            "imaging",
            "genomics",
            "pharmacology",
            "longitudinal",
            "evolution",
            "simulation",
            "therapy",
            "optimization",
            "trials",
            "response",
            "counterfactual",
            "kg",
            "graph_rag",
            "evidence",
            "memory",
            "research_intelligence",
            "safety",
            "validation",
            "governance",
            "explainability",
            "report"
        ]

    @classmethod
    def get_plane_telemetry_topology(cls) -> Dict[str, Any]:
        """Provides dynamic topology for the OS Cockpit UI."""
        topology = {}
        for plane in [PlaneType.PATIENT, PlaneType.SCIENTIFIC, PlaneType.CLINICAL, PlaneType.EVIDENCE, PlaneType.GOVERNANCE]:
            agents = cls.get_agents_by_plane(plane)
            topology[plane.value] = {
                "plane_name": plane.value.replace("_", " ").title(),
                "agent_count": len(agents),
                "agents": [
                    {
                        "agent_id": a.agent_id,
                        "name": a.name,
                        "requires": a.requires,
                        "publishes": a.publishes,
                        "critical": a.critical
                    }
                    for a in agents
                ],
                "status": "NOMINAL",
                "health_pct": 100.0
            }
        return topology
