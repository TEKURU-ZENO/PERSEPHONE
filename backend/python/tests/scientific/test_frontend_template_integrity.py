"""
Automated Frontend Template Integrity Test Suite
Comprehensive regex pattern scanner across all frontend components.
Verifies that frontend component templates do NOT contain hardcoded clinical results,
fabricated p-values, static rates (/day), static volumes (cm³), or ungrounded statistics.
"""

import os
import re
import unittest
from backend.python.compute.counterfactual.comparison import CounterfactualComparator

def get_repo_root():
    current = os.path.abspath(os.path.dirname(__file__))
    while current and not os.path.exists(os.path.join(current, 'frontend')):
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return current

REPO_ROOT = get_repo_root()


def strip_interpolations(text: str) -> str:
    """Strips ${...} interpolations from template strings, respecting nested braces."""
    result = []
    i = 0
    n = len(text)
    while i < n:
        if text[i:i+2] == '${':
            brace_depth = 1
            i += 2
            while i < n and brace_depth > 0:
                if text[i] == '{':
                    brace_depth += 1
                elif text[i] == '}':
                    brace_depth -= 1
                i += 1
        else:
            result.append(text[i])
            i += 1
    return ''.join(result)


class TestFrontendTemplateIntegrity(unittest.TestCase):
    """
    Automated pattern scanner guarding all component templates against hardcoded
    clinical results, static rates, fake p-values, and invented statistics.
    """

    def setUp(self):
        self.components_dir = os.path.join(
            REPO_ROOT, "frontend", "apps", "dashboard", "src", "components"
        )
        self.assertTrue(
            os.path.exists(self.components_dir),
            f"Components directory not found: {self.components_dir}"
        )

    def test_all_components_scanned_for_static_clinical_patterns(self):
        """
        Scans EVERY .js component in frontend/apps/dashboard/src/components/ for prohibited
        static clinical result patterns in templates.
        """
        component_files = []
        for root, _, files in os.walk(self.components_dir):
            for f in files:
                if f.endswith('.js'):
                    component_files.append(os.path.join(root, f))

        self.assertGreaterEqual(len(component_files), 20, "Must scan all dashboard component files")

        # Prohibited regex patterns for ungrounded results inside static template text
        pattern_rates = re.compile(r'[+-]?\d+\.?\d*\s*/day')
        pattern_volumes = re.compile(r'[+-]?\d+\.?\d*\s*cm³')
        pattern_pvals = re.compile(r'\bp\s*=\s*0\.\d+')
        pattern_static_hr = re.compile(r'\bHR\s*[:=]?\s*\d+\.\d+')
        pattern_static_ci_vals = re.compile(r'95%\s*CI\s*[:=]?\s*\[?\d+\.\d+')
        pattern_bracket_ci = re.compile(r'>\s*0\.\d{2}\s*\[0\.\d{2}\s*-\s*0\.\d{2}\]\s*<')

        # Minimal allowlist for genuine published literature citations and fixed registry prior constants
        literature_citation_allowlist = {
            "ResearchIntelligencePanel.js": [
                "HR 0.30",
                "95% CI 0.23"
            ]
        }

        violations = []

        for file_path in component_files:
            file_name = os.path.basename(file_path)
            rel_path = os.path.relpath(file_path, self.components_dir)

            with open(file_path, 'r', encoding='utf-8') as f:
                raw_content = f.read()

            # Strip all ${...} dynamic interpolations
            stripped = strip_interpolations(raw_content)

            # Strip HTML tag attributes (style, class, id)
            clean = re.sub(r'style="[^"]*"', '', stripped)
            clean = re.sub(r"style='[^']*'", '', clean)
            clean = re.sub(r'class="[^"]*"', '', clean)
            clean = re.sub(r'id="[^"]*"', '', clean)

            # 1. Prohibited volumetric rates (e.g., 0.0147/day, +0.004/day, -0.05 cm³/day)
            rate_matches = pattern_rates.findall(clean)
            if rate_matches:
                violations.append(f"{rel_path}: Found static rate(s) {rate_matches}")

            # 2. Prohibited volumes (e.g., 8.0 cm³, 82.0 cm³)
            vol_matches = pattern_volumes.findall(clean)
            if vol_matches:
                violations.append(f"{rel_path}: Found static volume(s) {vol_matches}")

            # 3. Prohibited static p-values (e.g., p = 0.0014, p = 0.0035)
            pval_matches = pattern_pvals.findall(clean)
            if pval_matches:
                violations.append(f"{rel_path}: Found static p-value(s) {pval_matches}")

            # 4. Prohibited static hazard ratios (excluding allowlisted literature citations)
            hr_matches = pattern_static_hr.findall(clean)
            allowed_hrs = literature_citation_allowlist.get(file_name, [])
            filtered_hrs = [m for m in hr_matches if not any(a in m for a in allowed_hrs)]
            if filtered_hrs:
                violations.append(f"{rel_path}: Found static hazard ratio(s) {filtered_hrs}")

            # 5. Prohibited static 95% CI numeric values
            ci_matches = pattern_static_ci_vals.findall(clean)
            allowed_cis = literature_citation_allowlist.get(file_name, [])
            filtered_cis = [m for m in ci_matches if not any(a in m for a in allowed_cis)]
            if filtered_cis:
                violations.append(f"{rel_path}: Found static 95% CI value(s) {filtered_cis}")

            # 6. Prohibited bracketed CI results (e.g., >0.67 [0.44 - 0.98]<)
            bracket_matches = pattern_bracket_ci.findall(clean)
            if bracket_matches:
                violations.append(f"{rel_path}: Found bracketed CI result(s) {bracket_matches}")

        self.assertEqual(
            violations, [],
            f"Frontend template integrity violations detected:\n" + "\n".join(violations)
        )

    def test_scenario_lab_no_fabricated_narratives_or_static_winners(self):
        """CounterfactualLabPanel must not contain fabricated winner banner or ungrounded rationale fallback."""
        cf_path = os.path.join(self.components_dir, "counterfactual", "CounterfactualLabPanel.js")
        with open(cf_path, "r", encoding="utf-8") as f:
            content = f.read()

        prohibited_narratives = [
            "+38.5 days median TTP gain",
            "reducing cumulative toxic dose burden by 34.2%",
            "Intermittent dose vacations preserve drug-sensitive clones",
            "Best-performing under simulated biophysical Lotka-Volterra assumptions"
        ]
        for s in prohibited_narratives:
            self.assertNotIn(s, content, f"Prohibited narrative found in CounterfactualLabPanel.js: '{s}'")

        # Line 611 fallback must be em-dash
        self.assertIn("${best.rationale || '—'}", content)
        self.assertIn("${best.qualification || '—'}", content)

    def test_response_kinetics_and_biomarkers_initialized_with_em_dash(self):
        """ResponseIntelligencePanel must initialize pre-fetch kinetics and biomarker cards with '—'."""
        resp_path = os.path.join(self.components_dir, "response", "ResponseIntelligencePanel.js")
        with open(resp_path, "r", encoding="utf-8") as f:
            content = f.read()

        # KPI cards
        self.assertIn('id="val-orr">—<', content)
        self.assertIn('id="val-dcr">—<', content)
        self.assertIn('id="val-pfs">—<', content)

        # Kinetics placeholders
        self.assertIn('id="kin-kc">—<', content)
        self.assertIn('id="kin-tnadir">—<', content)
        self.assertIn('id="kin-vnadir">—<', content)
        self.assertIn('id="kin-rebound">—<', content)

        # Prohibited old static numbers
        self.assertNotIn('0.0147/day', content)
        self.assertNotIn('8.0 cm³ (−90.2%)', content)
        self.assertNotIn('+0.004/day', content)

    def test_genomics_pathways_and_signatures_initialized_with_em_dash(self):
        """GenomicLabPanel must not contain static pathway p-values and must initialize signatures with '—'."""
        gen_path = os.path.join(self.components_dir, "genomics", "GenomicLabPanel.js")
        with open(gen_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Prohibited static pathway results
        self.assertNotIn('p = 0.0014', content)
        self.assertNotIn('p = 0.0035', content)
        self.assertNotIn('p = 0.0028', content)
        self.assertNotIn('p = 0.0060', content)

        # Signatures placeholders
        self.assertIn('id="sig-tmb">—<', content)
        self.assertIn('id="sig-msi">—<', content)
        self.assertIn('id="sig-dom">—<', content)

    def test_clinical_monitoring_initialized_with_em_dash(self):
        """ClinicalMonitoringPanel must initialize trajectory cards with '—'."""
        mon_path = os.path.join(self.components_dir, "monitoring", "ClinicalMonitoringPanel.js")
        with open(mon_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn('id="traj-base-vol">—<', content)
        self.assertIn('id="traj-nadir-vol">—<', content)
        self.assertIn('id="traj-cur-vol">—<', content)
        self.assertIn('id="traj-cur-vel">—<', content)

        # Prohibited old static trajectory numbers
        self.assertNotIn('>82.0 cm³<', content)
        self.assertNotIn('>8.0 cm³<', content)
        self.assertNotIn('>+0.10 cm³/day<', content)

    def test_counterfactual_comparison_drops_deprecated_keys(self):
        """Backend CounterfactualComparator must not return deprecated keys average_treatment_effect or causal_manifest."""
        simulation_output = {
            "arm_results": {
                "mtd": [{"progressed": False, "ttp": 180.0}],
                "adaptive": [{"progressed": False, "ttp": 180.0}]
            }
        }
        outcomes_by_arm = {
            "mtd": {"median_pfs_days": 180.0},
            "adaptive": {"median_pfs_days": 180.0}
        }
        res = CounterfactualComparator.compare_arms(
            simulation_output=simulation_output,
            outcomes_by_arm=outcomes_by_arm,
            control_arm="mtd"
        )
        comparisons = res.get("comparisons", {})
        adaptive_comp = comparisons.get("adaptive", {})

        # Assert deprecated keys are completely dropped
        self.assertNotIn("average_treatment_effect", adaptive_comp)
        self.assertNotIn("causal_manifest", adaptive_comp)

        # Assert modern keys exist
        self.assertIn("delta_ttp", adaptive_comp)
        self.assertIn("scenario_manifest", adaptive_comp)


if __name__ == '__main__':
    unittest.main()
