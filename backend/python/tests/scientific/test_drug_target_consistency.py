"""
PERSEPHONE Automated Clinical and Drug-Target Consistency Test Suite
Permanently guards against clinical misinformation, target mismatches,
and guideline hallucinations.
"""

import os
import sys
import json
import csv
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

    def test_clinical_trials_json_consistency(self):
        """clinical_trials.json must strictly match actual clinical trial protocols."""
        trials_path = os.path.join(self.root, "datasets", "knowledge", "clinical_trials.json")
        with open(trials_path, "r", encoding="utf-8") as f:
            trials = json.load(f)

        trial_map = {t["trialId"]: t for t in trials}

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

        # CHRYSALIS-2 (NCT04077463)
        chrysalis = trial_map.get("NCT04077463")
        self.assertIsNotNone(chrysalis)
        self.assertIn("EGFR", chrysalis["biomarkers"])

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

        # In adagrasib entry, ensure 'kras g12d inhibitor' does not appear
        self.assertNotIn('"kras g12d inhibitor"', content)
        self.assertIn('"kras g12c inhibitor"', content)
        self.assertIn('"kras g12d inhibitor (discontinued)"', content)

    def test_patients_js_clinical_truth(self):
        """patients.js must reflect correct oncological staging, guidelines, and nomenclature."""
        patients_path = os.path.join(self.root, "frontend", "apps", "dashboard", "src", "data", "patients.js")
        with open(patients_path, "r", encoding="utf-8") as f:
            content = f.read()

        # HGVS 3-letter amino acid code validation
        self.assertNotIn('"p.Gly12D"', content)
        self.assertNotIn('"p.Leu858R"', content)
        self.assertNotIn('"p.Thr790M"', content)
        self.assertIn('"p.Gly12Asp"', content)
        self.assertIn('"p.Leu858Arg"', content)

        # Patient A MYC classification
        self.assertIn('tier: "Tier III (unknown clinical significance)"', content)
        self.assertNotIn('classification: "VUS"', content)

        # Patient B acquired MET amplification bypass
        self.assertIn('"MET"', content)
        self.assertIn('NCT03944772', content)

        # Patient C must continue FOLFIRI + bevacizumab (no adagrasib)
        self.assertNotIn('"adagrasib + cetuximab"', content.lower())
        self.assertTrue(
            "folfiri + bevacizumab" in content.lower() and "continue" in content.lower(),
            "patients.js must recommend continuing FOLFIRI + bevacizumab for Patient C"
        )

    def test_cosmic_sbs96_reference_sanity(self):
        """COSMIC v3.4 SBS reference matrix must exhibit expected biological mutation profiles."""
        csv_path = os.path.join(self.root, "datasets", "reference", "cosmic_sbs96_reference.csv")
        self.assertTrue(os.path.exists(csv_path), "cosmic_sbs96_reference.csv must exist")

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        self.assertEqual(len(rows), 96, "COSMIC SBS reference must have exactly 96 trinucleotide contexts")
        self.assertIn("SBS1", rows[0])
        self.assertIn("SBS3", rows[0])
        self.assertIn("SBS7a", rows[0])

        # SBS1 is characterized by spontaneous deamination of 5-methylcytosine at CpG sites:
        # A[C>T]G, C[C>T]G, G[C>T]G, T[C>T]G
        cpg_types = {"A[C>T]G", "C[C>T]G", "G[C>T]G", "T[C>T]G"}
        sbs1_cpg_sum = sum(float(r["SBS1"]) for r in rows if r["Type"] in cpg_types)
        sbs1_total = sum(float(r["SBS1"]) for r in rows)
        cpg_fraction = sbs1_cpg_sum / sbs1_total

        self.assertGreater(
            cpg_fraction, 0.70,
            f"SBS1 clock signature must be dominated by NpCpG contexts (>70%), got {cpg_fraction:.2%}"
        )

        # SBS7a is UV-induced dipyrimidine photoproduct signature:
        # High peaks at C[C>T]C, C[C>T]T, T[C>T]C, T[C>T]T
        uv_types = {"C[C>T]C", "C[C>T]T", "T[C>T]C", "T[C>T]T"}
        sbs7a_uv_sum = sum(float(r["SBS7a"]) for r in rows if r["Type"] in uv_types)
        sbs7a_total = sum(float(r["SBS7a"]) for r in rows)
        uv_fraction = sbs7a_uv_sum / sbs7a_total

        self.assertGreater(
            uv_fraction, 0.40,
            f"SBS7a UV signature must be dominated by dipyrimidine C>T contexts (>40%), got {uv_fraction:.2%}"
        )


if __name__ == "__main__":
    unittest.main()
