"""
PERSEPHONE Automated Clinical and Drug-Target Consistency Test Suite
Permanently guards against clinical misinformation, target mismatches,
and guideline hallucinations.
"""

import os
import sys
import json
import csv
import hashlib
import unittest

def get_repo_root():
    current = os.path.abspath(os.path.dirname(__file__))
    while current and not os.path.exists(os.path.join(current, 'datasets')):
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return current

REPO_ROOT = get_repo_root()
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from backend.python.compute.graph.pathfinding import build_graph
from backend.python.compute.multimodal.pathology.segmentor import TumorSegmentor


class TestDrugTargetConsistency(unittest.TestCase):
    def setUp(self):
        self.root = REPO_ROOT

    def test_pathfinding_graph_drug_targets(self):
        """Knowledge graph pathfinding edges must be biochemically accurate."""
        nodes, edges = build_graph()

        # 1. Adagrasib and Sotorasib must NEVER target KRAS G12D
        for edge in edges:
            source = edge.get("source", "").lower()
            target = edge.get("target", "").lower()
            if source in ("adagrasib", "sotorasib"):
                self.assertNotEqual(
                    target, "kras-g12d",
                    f"CRITICAL BIOMEDICAL ERROR: {source} cannot inhibit KRAS G12D"
                )

        # 2. MRTX1133 targets KRAS G12D but must be marked discontinued
        mrtx_targets = [e for e in edges if e.get("source") == "mrtx1133" and e.get("target") == "kras-g12d"]
        self.assertTrue(len(mrtx_targets) > 0, "mrtx1133 must have a target edge to kras-g12d")

        # Drugbank status check for MRTX1133
        drugbank_path = os.path.join(self.root, "datasets", "knowledge", "drugbank.json")
        with open(drugbank_path, "r", encoding="utf-8") as f:
            drugbank = json.load(f)
        mrtx_entry = next((d for d in drugbank if d.get("name", "").lower() == "mrtx1133"), None)
        self.assertIsNotNone(mrtx_entry, "mrtx1133 must exist in drugbank.json")
        self.assertIn("discontinued", mrtx_entry.get("status", "").lower(), "mrtx1133 must be marked discontinued")

        # 3. Adagrasib targets KRAS G12C
        adagrasib_g12c = [e for e in edges if e.get("source") == "adagrasib" and e.get("target") == "kras-g12c"]
        self.assertTrue(len(adagrasib_g12c) > 0, "adagrasib must target kras-g12c")

        # 4. Savolitinib targets MET amplification bypass
        savo_targets = [e for e in edges if e.get("source") == "savolitinib" and e.get("target") == "met-amp"]
        self.assertTrue(len(savo_targets) > 0, "savolitinib must target met-amp")

        # 5. Patient B mutations: MET amplification, NOT T790M
        patient_b_mutations = [e.get("target") for e in edges if e.get("source") == "patient-b" and e.get("type") == "has_mutation"]
        self.assertIn("met-amp", patient_b_mutations, "patient-b must have acquired met-amp")
        self.assertNotIn("egfr-t790m", patient_b_mutations, "patient-b must not have egfr-t790m")

        # 6. Patient A trial enrolls: NCT03737643 (DUO-O), NOT unverified NCT04381884
        trial_enrolls = [e.get("source") for e in edges if e.get("target") == "brca1-mut" and e.get("type") == "enrolls"]
        self.assertIn("NCT03737643", trial_enrolls, "DUO-O trial must enroll brca1-mut")
        self.assertNotIn("NCT04381884", trial_enrolls, "Unverified COVID trial NCT04381884 must not enroll brca1-mut")

    def test_frontend_graph_service_edges(self):
        """Frontend graph.service.js must not contain fabricated target edges."""
        graph_service_path = os.path.join(self.root, "frontend", "apps", "dashboard", "src", "services", "graph.service.js")
        with open(graph_service_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertNotIn(
            "source: 'adagrasib', target: 'kras-g12d'",
            content,
            "graph.service.js must not target adagrasib to kras-g12d"
        )
        self.assertIn("source: 'adagrasib', target: 'kras-g12c'", content)
        self.assertIn("source: 'savolitinib', target: 'met-amp'", content)
        self.assertIn("source: 'mrtx1133', target: 'kras-g12d'", content)
        self.assertIn("source: 'NCT03737643', target: 'brca1-mut'", content)
        self.assertNotIn("source: 'NCT04381884'", content)

    def test_clinical_trials_json_consistency(self):
        """clinical_trials.json must strictly match actual clinical trial protocols."""
        trials_path = os.path.join(self.root, "datasets", "knowledge", "clinical_trials.json")
        with open(trials_path, "r", encoding="utf-8") as f:
            trials = json.load(f)

        trial_map = {t["trialId"]: t for t in trials}

        # DUO-O (NCT03737643)
        duo_o = trial_map.get("NCT03737643")
        self.assertIsNotNone(duo_o, "DUO-O (NCT03737643) must exist in clinical_trials.json")
        self.assertIn("BRCA1", duo_o["biomarkers"])
        self.assertIn("Active, not recruiting", duo_o["status"])

        # Hallucinated trial IDs must NOT exist
        self.assertNotIn("NCT04381884", trial_map)
        self.assertNotIn("NCT05206253", trial_map)

        # KRYSTAL-10 (NCT04625881)
        krystal10 = trial_map.get("NCT04625881")
        self.assertIsNotNone(krystal10)
        self.assertIn("KRAS G12C", krystal10["biomarkers"])
        self.assertNotIn("KRAS G12D", krystal10["biomarkers"])

        # KRYSTAL-1 (NCT03785249)
        krystal1 = trial_map.get("NCT03785249")
        self.assertIsNotNone(krystal1)
        self.assertIn("KRAS G12C", krystal1["biomarkers"])
        self.assertNotIn("KRAS G12D", krystal1["biomarkers"])

        # CodeBreaK 300 (NCT04613596)
        codebreak = trial_map.get("NCT04613596")
        self.assertIsNotNone(codebreak)
        self.assertIn("KRAS G12C", codebreak["biomarkers"])
        self.assertNotIn("KRAS G12D", codebreak["biomarkers"])

        # ORCHARD (NCT03944772)
        orchard = trial_map.get("NCT03944772")
        self.assertIsNotNone(orchard)
        self.assertIn("MET", orchard["biomarkers"])
        self.assertIn("Active, not recruiting", orchard["status"])

        # CHRYSALIS-2 (NCT04077463)
        chrysalis = trial_map.get("NCT04077463")
        self.assertIsNotNone(chrysalis)
        self.assertIn("EGFR", chrysalis["biomarkers"])
        self.assertIn("Active, not recruiting", chrysalis["status"])
        self.assertIn("platinum", chrysalis["enrollmentCriteria"].lower())

        # MRTX1133 must NOT be in active recruiting trials
        for t in trials:
            self.assertNotIn(
                "MRTX1133", t.get("drugs", []),
                f"Discontinued drug MRTX1133 should not be in clinical trials list: {t['trialId']}"
            )

    def test_concept_registry_aliases(self):
        """concept-registry.js must not map G12D aliases to Adagrasib."""
        registry_path = os.path.join(self.root, "frontend", "apps", "dashboard", "src", "data", "concept-registry.js")
        with open(registry_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertNotIn('"kras g12d inhibitor"', content)
        self.assertIn('"kras g12c inhibitor"', content)
        self.assertIn('"kras g12d inhibitor (discontinued)"', content)

    def test_patients_js_clinical_truth(self):
        """patients.js must reflect correct oncological staging, guidelines, and nomenclature."""
        patients_path = os.path.join(self.root, "frontend", "apps", "dashboard", "src", "data", "patients.js")
        with open(patients_path, "r", encoding="utf-8") as f:
            content = f.read()

        # matchScore must NOT be present in patient fixtures
        self.assertNotIn('matchScore', content, "matchScore must be replaced with clinical eligibility in patient fixtures")

        # HGVS 3-letter amino acid code validation
        self.assertNotIn('"p.Gly12D"', content)
        self.assertNotIn('"p.Leu858R"', content)
        self.assertNotIn('"p.Thr790M"', content)
        self.assertIn('"p.Gly12Asp"', content)
        self.assertIn('"p.Leu858Arg"', content)

        # Patient A verified trials and somatic tier
        self.assertIn('NCT03737643', content)
        self.assertIn('NCT04644068', content)
        self.assertNotIn('NCT04381884', content)
        self.assertNotIn('NCT05206253', content)
        self.assertIn('tier: "Tier III (unknown clinical significance)"', content)

        # Patient B acquired MET amplification bypass: high-level CN=12 and somatic tier
        self.assertIn('CN=12', content)
        self.assertNotIn('CN=5', content)
        self.assertIn('High-Level Amplification (CN=12)', content)
        self.assertIn('Tier I (Level B: NCCN Guidelines NSCLC v1.2024', content)
        self.assertIn('NCT03944772', content)
        self.assertIn('platinum', content)

        # Patient C must continue FOLFIRI + bevacizumab (no adagrasib)
        self.assertNotIn('"adagrasib + cetuximab"', content.lower())
        self.assertTrue(
            "folfiri + bevacizumab" in content.lower() and "continue" in content.lower(),
            "patients.js must recommend continuing FOLFIRI + bevacizumab for Patient C"
        )

    def test_pathology_segmentor_integrity(self):
        """TumorSegmentor must honestly flag mock mode and compartments must strictly sum to <= 100%."""
        mock_res = TumorSegmentor.segment_patch({"test": "patch_data"})
        self.assertTrue(mock_res.get("is_mock", False), "Standalone segmentor must flag is_mock: True")
        self.assertNotIn("confidence", mock_res, "Mock segmentor must NOT fabricate confidence metrics")

        # Invariance test: 1,000 distinct pseudo-random inputs
        for i in range(1000):
            res = TumorSegmentor.segment_patch(f"patch_sample_context_{i}")
            tissue_sum = res["tumor_area_fraction"] + res["necrosis_area_fraction"] + res["stroma_area_fraction"]
            self.assertLessEqual(tissue_sum, 1.0, f"Tissue compartments exceed 1.0: {tissue_sum}")
            total_sum = tissue_sum + res["background_area_fraction"]
            self.assertAlmostEqual(total_sum, 1.0, places=3)

    def test_parameter_registry_citations(self):
        """parameter-registry.json must contain authentic PMIDs and transparent conceptual references."""
        reg_path = os.path.join(self.root, "research", "parameter-registry.json")
        with open(reg_path, "r", encoding="utf-8") as f:
            registry = json.load(f)

        # alpha1: Gatenby 2009 authentic PMID 19487300
        self.assertEqual(registry["alpha1"]["source_type"], "assumed")
        self.assertIn("19487300", registry["alpha1"]["conceptual_reference"])
        self.assertNotIn("19447936", registry["alpha1"].get("conceptual_reference", ""))

        # alpha2: assumed, Silva/Gatenby 2010 authentic PMID 20406443, no fake melanoma PMID 20959481 or Silk 26500125
        self.assertEqual(registry["alpha2"]["source_type"], "assumed")
        self.assertIn("20406443", registry["alpha2"]["conceptual_reference"])
        self.assertNotIn("20959481", registry["alpha2"].get("conceptual_reference", ""))
        self.assertNotIn("26500125", registry["alpha2"].get("conceptual_reference", ""))

        # ES: Garnett 2012 authentic PMID 22460902, marked assumed
        self.assertEqual(registry["ES"]["source_type"], "assumed")
        self.assertIn("22460902", registry["ES"]["conceptual_reference"])

        # ER: Engelman 2007 authentic PMID 17463250
        self.assertEqual(registry["ER"]["source_type"], "assumed")
        self.assertIn("17463250", registry["ER"]["conceptual_reference"])

        # K: Michor 2004 authentic PMID 14993901
        self.assertEqual(registry["K"]["source_type"], "assumed")
        self.assertIn("14993901", registry["K"]["conceptual_reference"])
        self.assertNotIn("15281884", registry["K"].get("conceptual_reference", ""))

    def test_agent_layer_trial_cancer_type_matching(self):
        """Agents must never assign trials or citations across mismatched cancer types."""
        # 1. Verify ai/agents/evidence/index.js derives trials from patient fixture and contains NO hardcoded cross-patient fallback
        evidence_agent_path = os.path.join(self.root, "ai", "agents", "evidence", "index.js")
        with open(evidence_agent_path, "r", encoding="utf-8") as f:
            evidence_code = f.read()

        self.assertNotIn(
            "patient.id === 'patient-a' ? [\"NCT03737643\"] : [\"NCT03944772\"]",
            evidence_code,
            "CRITICAL BUG: Evidence agent must not map non-patient-a cases to lung trial NCT03944772"
        )
        self.assertIn("patient.trials", evidence_code)
        self.assertIn("patient.citations", evidence_code)

        # 2. Verify patients.js digital twin fixtures have strictly matched cancer-type trials and citations
        patients_js_path = os.path.join(self.root, "frontend", "apps", "dashboard", "src", "data", "patients.js")
        with open(patients_js_path, "r", encoding="utf-8") as f:
            patients_js = f.read()

        # Split eligibility and recruitment_status verification
        self.assertIn("recruitment_status", patients_js, "patients.js must specify recruitment_status")
        self.assertIn("eligibility", patients_js, "patients.js must specify eligibility")

        # Patient C (colorectal) must NEVER match lung trial NCT03944772 or ovarian trial NCT03737643
        patient_c_chunk = patients_js[patients_js.find('"patient-c"'):]
        self.assertNotIn("NCT03944772", patient_c_chunk, "Colorectal patient must not match lung trial NCT03944772")
        self.assertNotIn("NCT03737643", patient_c_chunk, "Colorectal patient must not match ovarian trial NCT03737643")
        self.assertNotIn("NCT04077463", patient_c_chunk, "Colorectal patient must not match NSCLC trial NCT04077463")

        # Patient A (ovarian) must NOT receive lung trial NCT03944772 or Engelman MET paper (17463250)
        patient_a_chunk = patients_js[patients_js.find('"patient-a"'):patients_js.find('"patient-b"')]
        self.assertNotIn("NCT03944772", patient_a_chunk, "Ovarian patient must not match lung trial NCT03944772")
        self.assertNotIn("17463250", patient_a_chunk, "Ovarian patient must not cite MET paper 17463250")
        self.assertIn("30345884", patient_a_chunk, "Ovarian patient must cite SOLO-1 NEJM paper (30345884)")

        # Patient B (lung) must receive EGFR/MET trials (NCT03944772, NCT04077463) and MET paper (17463250)
        patient_b_chunk = patients_js[patients_js.find('"patient-b"'):patients_js.find('"patient-c"')]
        self.assertIn("NCT03944772", patient_b_chunk)
        self.assertIn("NCT04077463", patient_b_chunk)
        self.assertNotIn("NCT03737643", patient_b_chunk, "Lung patient must not match ovarian trial NCT03737643")
        self.assertIn("17463250", patient_b_chunk, "Lung patient must cite Engelman MET paper (17463250)")

    def test_no_fallback_trial_ids(self):
        """Core compute engines must default to None when no trial is matched, never inserting NCT03737643."""
        # 1. ResponseIntelligenceAgent with no matched trial
        from backend.python.compute.ai_runtime.agents.instances.response_intelligence_agent import ResponseIntelligenceAgent
        class MockBlackboard:
            def read(self, key):
                return None
        agent = ResponseIntelligenceAgent()
        agent.initialize(MockBlackboard())
        agent.plan(MockBlackboard())
        self.assertIsNone(
            agent.payload["trials"]["top_trial_id"],
            "ResponseIntelligenceAgent must default top_trial_id to None when no trial is matched"
        )

        # 2. MultimodalResponseFusion with no matched trial
        from backend.python.compute.response_intelligence.fusion import MultimodalResponseFusion
        fused = MultimodalResponseFusion.fuse({"trials": {}})
        self.assertIsNone(
            fused.trial["top_trial_id"].value,
            "MultimodalResponseFusion must default top_trial_id to None when no trial is matched"
        )
        self.assertTrue(fused.trial["top_trial_id"].missingness)

        # 3. TreatmentMatrix trial_protocol regimen
        from backend.python.compute.counterfactual.treatment_matrix import TreatmentMatrix
        trial_arm = TreatmentMatrix.get_regimen("trial_protocol")
        self.assertNotIn(
            "NCT03737643", trial_arm["name"],
            "TreatmentMatrix trial_protocol must not have hardcoded NCT03737643 in name"
        )

        # 4. Verify runtime.py does not hardcode NCT03737643 as fallback
        runtime_path = os.path.join(self.root, "backend", "python", "compute", "ai_runtime", "agents", "runtime.py")
        with open(runtime_path, "r", encoding="utf-8") as f:
            runtime_code = f.read()
        self.assertNotIn(
            "top_trial.get('trialId', 'NCT03737643')",
            runtime_code,
            "runtime.py must not fallback to NCT03737643"
        )

    def test_cosmic_sbs96_reference_sanity(self):
        """COSMIC v3.4 SBS reference matrix must exhibit expected biological mutation profiles and canonical LF hash."""
        csv_path = os.path.join(self.root, "datasets", "reference", "cosmic_sbs96_reference.csv")
        self.assertTrue(os.path.exists(csv_path), "cosmic_sbs96_reference.csv must exist")

        with open(csv_path, "rb") as f:
            content = f.read()

        # Compute hash with LF line endings
        lf_content = content.replace(b"\r\n", b"\n")
        lf_hash = hashlib.sha256(lf_content).hexdigest()
        self.assertEqual(
            lf_hash,
            "aad0be68be61cb94674d8c5c01309f7ab9670cfcd610966d00b3f0883feeec72",
            "COSMIC CSV LF SHA-256 must match authentic AlexandrovLab dataset"
        )

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        self.assertEqual(len(rows), 96, "COSMIC SBS reference must have exactly 96 trinucleotide contexts")
        self.assertIn("SBS1", rows[0])
        self.assertIn("SBS3", rows[0])
        self.assertIn("SBS7a", rows[0])

        # SBS1 CpG deamination peaks
        cpg_types = {"A[C>T]G", "C[C>T]G", "G[C>T]G", "T[C>T]G"}
        sbs1_cpg_sum = sum(float(r["SBS1"]) for r in rows if r["Type"] in cpg_types)
        sbs1_total = sum(float(r["SBS1"]) for r in rows)
        cpg_fraction = sbs1_cpg_sum / sbs1_total
        self.assertGreater(cpg_fraction, 0.70)

        # SBS7a UV dipyrimidine peaks
        uv_types = {"C[C>T]C", "C[C>T]T", "T[C>T]C", "T[C>T]T"}
        sbs7a_uv_sum = sum(float(r["SBS7a"]) for r in rows if r["Type"] in uv_types)
        sbs7a_total = sum(float(r["SBS7a"]) for r in rows)
        uv_fraction = sbs7a_uv_sum / sbs7a_total
        self.assertGreater(uv_fraction, 0.40)


if __name__ == "__main__":
    unittest.main()
