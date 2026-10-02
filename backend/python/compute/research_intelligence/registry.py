"""
Research Intelligence Registry module for PERSEPHONE.
Provides unified orchestration, latency profiling, and execution dispatch for ClinicalEvidenceGraph,
literature retrieval, versioned guideline evaluation, contradiction scanning, and Merkle lineage tracing.
"""
import time
from typing import Dict, List, Any, Optional

from backend.python.compute.research_intelligence.graph.evidence_graph import ClinicalEvidenceGraph
from backend.python.compute.research_intelligence.graph.traverser import EvidenceGraphTraverser
from backend.python.compute.research_intelligence.literature.retrieval import LiteratureRetriever
from backend.python.compute.research_intelligence.literature.evidence import EvidenceExtractor
from backend.python.compute.research_intelligence.literature.citation import CitationManager
from backend.python.compute.research_intelligence.guidelines.recommendation import GuidelineRecommender
from backend.python.compute.research_intelligence.trials.evidence_linker import TrialEvidenceLinker
from backend.python.compute.research_intelligence.knowledge.hypothesis import ClinicalHypothesisGenerator
from backend.python.compute.research_intelligence.knowledge.contradiction import ContradictionDetector
from backend.python.compute.research_intelligence.provenance.source import ProvenanceSource
from backend.python.compute.research_intelligence.provenance.evidence_item import EvidenceItem
from backend.python.compute.research_intelligence.provenance.claim import ClinicalClaim
from backend.python.compute.research_intelligence.provenance.snapshot import EvidenceSnapshot
from backend.python.compute.research_intelligence.provenance.grounding import GroundingGate
from backend.python.compute.research_intelligence.provenance.lineage import EvidenceLineageTracker


class ResearchIntelligenceRegistry:
    """
    Public registry interface for PERSEPHONE Research Intelligence compute pipelines.
    """

    @classmethod
    def assemble_evidence_graph(cls, patient_data: Optional[Dict[str, Any]] = None, proposed_drug: Optional[str] = None) -> Dict[str, Any]:
        """
        Assembles the authoritative first-class ClinicalEvidenceGraph connecting:
        Patient -> Variants -> Pathways -> Drugs -> Trials -> Publications -> Guidelines -> Claims
        """
        start = time.perf_counter()
        patient = patient_data or {"id": "patient-a", "diagnosis": "Ovarian Cancer", "stage": "Stage III", "variants": ["BRCA1"]}
        patient_id = patient.get("id", "patient-a")
        disease = patient.get("diagnosis", "Ovarian Cancer")
        variants = patient.get("variants", ["BRCA1"])
        drug = proposed_drug or ("Olaparib" if any("BRCA" in str(v).upper() for v in variants) else "Osimertinib")

        graph = ClinicalEvidenceGraph(f"graph-{patient_id}")

        # 1. Patient Node
        graph.add_node(patient_id, "PATIENT", f"Patient Twin: {patient.get('name', patient_id)}", {
            "disease": disease,
            "stage": patient.get("stage", "Stage III"),
            "age": patient.get("age", 58)
        })

        # 2. Variant Nodes
        for v in variants:
            v_id = f"var-{v.lower()}"
            graph.add_node(v_id, "VARIANT", f"Variant: {v}", {"gene": v, "classification": "Pathogenic"})
            graph.add_edge(patient_id, v_id, "HAS_VARIANT")

        # 3. Hypotheses & Pathway Nodes
        hypotheses = ClinicalHypothesisGenerator.generate_hypotheses(patient, [drug])
        for hyp in hypotheses:
            pw_id = f"pw-{hyp['pathway'].replace(' ', '-').lower()}"
            graph.add_node(pw_id, "PATHWAY", hyp["pathway"], {
                "mechanism": hyp["mechanism_type"],
                "target": hyp["target"],
                "plausibility": hyp["plausibility_score"]
            })
            for v in variants:
                graph.add_edge(f"var-{v.lower()}", pw_id, "ACTIVATES")

            # 4. Drug Node
            d_id = f"drug-{hyp['drug'].lower()}"
            graph.add_node(d_id, "DRUG", hyp["drug"], {"mechanism": hyp["mechanism_type"]})
            graph.add_edge(pw_id, d_id, "TARGETS")

        # 5. Literature Search
        papers = LiteratureRetriever.query({"patient": patient, "drug": drug})
        evidence_items: List[EvidenceItem] = []
        sources: List[ProvenanceSource] = []

        for p in papers[:4]:
            pmid = p.get("pmid")
            pub_id = f"pub-{pmid}"
            ev_data = p.get("evidence", {})
            hr_data = ev_data.get("hazard_ratio", {})
            hr_val = hr_data.get("value") if hr_data else None

            graph.add_node(pub_id, "PUBLICATION", f"PMID:{pmid} ({p.get('trial_name', 'Trial')})", {
                "title": p.get("title"),
                "journal": p.get("journal"),
                "year": p.get("year"),
                "citation": p.get("citation"),
                "phase": p.get("phase"),
                "hr": hr_val,
                "cebm_level": ev_data.get("quality_grading", {}).get("cebm_level")
            })

            # Connect Drug to Publication
            graph.add_edge(f"drug-{drug.lower()}", pub_id, "SUPPORTED_BY", {"evidence_level": ev_data.get("quality_grading", {}).get("cebm_level")})

            # Create ProvenanceSource & EvidenceItem
            src = ProvenanceSource(
                source_id=f"src-pmid-{pmid}",
                source_type="PUBMED",
                uri=p.get("identifiers", {}).get("urls", {}).get("pubmed_url", f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"),
                version=str(p.get("year")),
                title=p.get("title", "")
            )
            sources.append(src)

            ev_item = EvidenceItem(
                evidence_id=f"evd-{pmid}",
                source_id=src.source_id,
                source_hash=src.content_hash,
                study_design=ev_data.get("study_design", "Phase III RCT"),
                sample_size=ev_data.get("sample_size"),
                hazard_ratio=hr_data,
                median_pfs_delta_months=ev_data.get("median_pfs_delta_months"),
                cebm_level=ev_data.get("quality_grading", {}).get("cebm_level", "Level 1b"),
                grade_rating=ev_data.get("quality_grading", {}).get("grade_rating", "High"),
                summary_statement=p.get("citation", "")
            )
            evidence_items.append(ev_item)

            # 6. Trials Linking (NCT)
            nct_id = p.get("identifiers", {}).get("nct_id")
            if nct_id:
                t_id = f"trial-{nct_id.lower()}"
                graph.add_node(t_id, "TRIAL", f"{p.get('trial_name', 'Trial')} ({nct_id})", {
                    "phase": p.get("phase"),
                    "nct_id": nct_id
                })
                graph.add_edge(f"drug-{drug.lower()}", t_id, "STUDIED_IN")
                graph.add_edge(t_id, pub_id, "SUPPORTED_BY")

        # 7. Guidelines Matching
        guidelines = GuidelineRecommender.evaluate_patient_guidelines(patient, drug)
        for g in guidelines:
            g_id = f"guide-{g['rule_id'].lower()}"
            graph.add_node(g_id, "GUIDELINE", f"{g['organization']} {g['evidence_category']}", {
                "title": g["guideline_title"],
                "version": g["version"],
                "preference": g["preference_tier"],
                "category": g["evidence_category"],
                "rationale": g["rationale"],
                "url": g["source_url"]
            })
            graph.add_edge(f"drug-{drug.lower()}", g_id, "RECOMMENDED_BY")

            src_guide = ProvenanceSource(
                source_id=f"src-guide-{g['rule_id']}",
                source_type="GUIDELINE",
                uri=g["source_url"],
                version=g["version"],
                title=g["guideline_title"]
            )
            sources.append(src_guide)

        # 8. Contradiction Detection
        contradiction_res = ContradictionDetector.scan_contradictions(patient, drug, papers, guidelines)

        # 9. Clinical Claims Formulation & Grounding Gate
        claims = []
        lineage_manifests = []

        if guidelines:
            top_g = guidelines[0]
            claim_text = (
                f"Patient with {disease} harboring {', '.join(variants)} is indicated for "
                f"{drug} ({top_g['preference_tier']}, NCCN {top_g['evidence_category']})."
            )
            linked_ev_ids = [e.evidence_id for e in evidence_items]
            linked_src_ids = [s.source_id for s in sources]

            claim = ClinicalClaim(
                claim_id=f"CLAIM-{patient_id}-01",
                patient_id=patient_id,
                statement=claim_text,
                evidence_ids=linked_ev_ids,
                source_ids=linked_src_ids,
                generating_agent="Research Intelligence Agent",
                confidence=0.95,
                evidence_level="Level 1b",
                recommendation_category=top_g["evidence_category"]
            )

            # Evaluate with GroundingGate
            gate_res = GroundingGate.evaluate_claim(claim, evidence_items, contradiction_res.get("conflicts", []))
            claim.grounding_status = gate_res["grounding_status"]

            # Compute Hierarchical Merkle Lineage
            lineage = EvidenceLineageTracker.build_claim_lineage(claim, evidence_items, sources)
            lineage_manifests.append(lineage)

            # Add Claim Node to Graph
            c_node_id = f"claim-{claim.claim_id.lower()}"
            graph.add_node(c_node_id, "CLAIM", f"{claim.claim_id}: {claim.grounding_status}", claim.to_dict())
            graph.add_edge(f"drug-{drug.lower()}", c_node_id, "DERIVED_FROM")

            claims.append({
                "claim": claim.to_dict(),
                "grounding_gate": gate_res,
                "lineage": lineage
            })

        # 10. Agent Node
        agent_node_id = "agent-research-intel"
        graph.add_node(agent_node_id, "AGENT", "Research Intelligence Agent", {
            "version": "agent-v18",
            "classification": "Knowledge / Provenance"
        })
        if claims:
            graph.add_edge(agent_node_id, f"claim-{claims[0]['claim']['claim_id'].lower()}", "GENERATED_BY")

        # Snapshot creation for deterministic reproducibility
        snapshot = EvidenceSnapshot(
            snapshot_id=f"snap-{patient_id}-{int(time.time())}",
            source_id=f"sources-{len(sources)}",
            content_hash=lineage_manifests[0]["lineage_root_hash"] if lineage_manifests else "empty"
        )

        elapsed = round((time.perf_counter() - start) * 1000, 2)

        return {
            "evidence_graph": graph.to_dict(),
            "patient_context": {
                "patient_id": patient_id,
                "disease": disease,
                "variants": variants,
                "proposed_drug": drug
            },
            "hypotheses": hypotheses,
            "claims": claims,
            "guidelines": guidelines,
            "literature_papers": papers[:6],
            "contradiction_report": contradiction_res,
            "evidence_snapshot": snapshot.to_dict(),
            "lineage_manifests": lineage_manifests,
            "processingTimeMs": elapsed
        }

    @classmethod
    def query_literature(cls, query_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        start = time.perf_counter()
        papers = LiteratureRetriever.query(query_params)
        elapsed = round((time.perf_counter() - start) * 1000, 2)
        return {
            "query_params": query_params or {},
            "total_matches": len(papers),
            "publications": papers,
            "processingTimeMs": elapsed
        }

    @classmethod
    def evaluate_guidelines(cls, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        start = time.perf_counter()
        data = payload or {}
        patient = data.get("patient") or data.get("patient_data") or {"diagnosis": "Ovarian Cancer", "stage": "Stage III", "variants": ["BRCA1"]}
        drug = data.get("drug") or data.get("proposed_drug")
        recs = GuidelineRecommender.evaluate_patient_guidelines(patient, drug)
        elapsed = round((time.perf_counter() - start) * 1000, 2)
        return {
            "patient": patient,
            "matched_recommendations": recs,
            "recommendation_count": len(recs),
            "processingTimeMs": elapsed
        }

    @classmethod
    def detect_contradictions(cls, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        start = time.perf_counter()
        data = payload or {}
        patient = data.get("patient") or data.get("patient_data") or {"diagnosis": "Ovarian Cancer", "stage": "Stage III", "variants": ["BRCA1"]}
        drug = data.get("drug") or data.get("proposed_drug", "Olaparib")
        papers = LiteratureRetriever.query({"patient": patient, "drug": drug})
        guidelines = GuidelineRecommender.evaluate_patient_guidelines(patient, drug)
        res = ContradictionDetector.scan_contradictions(patient, drug, papers, guidelines)
        elapsed = round((time.perf_counter() - start) * 1000, 2)
        res["processingTimeMs"] = elapsed
        return res

    @classmethod
    def trace_provenance(cls, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        start = time.perf_counter()
        data = payload or {}
        patient_data = data.get("patient") or {"id": data.get("patientId", "patient-a"), "diagnosis": "Ovarian Cancer", "stage": "Stage III", "variants": ["BRCA1"]}
        graph_res = cls.assemble_evidence_graph(patient_data, data.get("drug"))
        elapsed = round((time.perf_counter() - start) * 1000, 2)
        return {
            "claims": graph_res.get("claims", []),
            "lineage_manifests": graph_res.get("lineage_manifests", []),
            "evidence_snapshot": graph_res.get("evidence_snapshot", {}),
            "processingTimeMs": elapsed
        }
