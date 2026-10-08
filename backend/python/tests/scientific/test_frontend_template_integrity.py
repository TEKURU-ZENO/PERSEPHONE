"""
Automated Frontend Template Integrity Test Suite
Verifies that frontend component templates do NOT contain hardcoded result numbers,
fabricated simulation claims, or ungrounded static statistics in initial HTML templates.
"""

import os
import re
import unittest

def get_repo_root():
    current = os.path.abspath(os.path.dirname(__file__))
    while current and not os.path.exists(os.path.join(current, 'frontend')):
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return current

REPO_ROOT = get_repo_root()

class TestFrontendTemplateIntegrity(unittest.TestCase):
    """
    Guards frontend component templates against fabricated defaults, static clinical claims,
    and invented simulation numbers.
    """

    def setUp(self):
        self.components_dir = os.path.join(
            REPO_ROOT, "frontend", "apps", "dashboard", "src", "components"
        )

    def test_scenario_lab_no_static_overclaims(self):
        """CounterfactualLabPanel must not contain fabricated result claims or static winner banners."""
        cf_path = os.path.join(self.components_dir, "counterfactual", "CounterfactualLabPanel.js")
        self.assertTrue(os.path.exists(cf_path), f"File {cf_path} must exist")

        with open(cf_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Prohibited hardcoded fabricated narrative strings
        prohibited_strings = [
            "+38.5 days median TTP gain",
            "reducing cumulative toxic dose burden by 34.2%",
            "+38.5 [+28.2 to +48.8] d",
            "+34.2% [+29.0% to +39.4%]",
            "-5.4 [-7.8 to -3.0]",
            "+44.0 [+32.0 to +56.0] d"
        ]

        for s in prohibited_strings:
            self.assertNotIn(
                s, content,
                f"Prohibited fabricated result string found in CounterfactualLabPanel.js: '{s}'"
            )

    def test_scenario_lab_initial_placeholders_use_em_dash(self):
        """CounterfactualLabPanel must initialize pre-fetch metric cards and tables with '—' or empty prompts."""
        cf_path = os.path.join(self.components_dir, "counterfactual", "CounterfactualLabPanel.js")
        with open(cf_path, "r", encoding="utf-8") as f:
            content = f.read()

        # KPI cards must default to em-dash in template
        self.assertIn('id="stat-v0">—<', content)
        self.assertIn('id="stat-k">—<', content)
        self.assertIn('id="stat-fr">—<', content)
        self.assertIn('id="stat-alpha">—<', content)
        self.assertIn('id="stat-es">—<', content)

        # Prohibited static KPI values
        self.assertNotIn('id="stat-v0">82.4', content)
        self.assertNotIn('id="stat-k">203.5', content)
        self.assertNotIn('id="stat-fr">5.2', content)

        # Survival endpoints table must not contain hardcoded static trial results in template
        self.assertNotIn('>88.5<', content)
        self.assertNotIn('>132.0<', content)
        self.assertNotIn('0.67 [0.44 - 0.98]', content)

        # Survival table must have an initial prompt row
        self.assertIn('Run simulation to project survival probabilities', content)
        self.assertIn('Run simulation to compute Kaplan-Meier step probabilities', content)

    def test_response_intelligence_initial_placeholders_use_em_dash(self):
        """ResponseIntelligencePanel must initialize pre-fetch metric cards with '—' rather than static numbers."""
        resp_path = os.path.join(self.components_dir, "response", "ResponseIntelligencePanel.js")
        self.assertTrue(os.path.exists(resp_path), f"File {resp_path} must exist")

        with open(resp_path, "r", encoding="utf-8") as f:
            content = f.read()

        # KPI cards must default to em-dash in template
        self.assertIn('id="val-orr">—<', content)
        self.assertIn('id="val-dcr">—<', content)
        self.assertIn('id="val-pfs">—<', content)
        self.assertIn('id="val-depth">—<', content)

        # Prohibited initial static numbers
        self.assertNotIn('id="val-orr">75.0%<', content)
        self.assertNotIn('id="val-dcr">93.0%<', content)
        self.assertNotIn('id="val-pfs">330.0', content)

    def test_no_hardcoded_hr_ci_patterns_in_static_templates(self):
        """Scans component templates to ensure hazard ratios and confidence intervals are not hardcoded in static HTML."""
        components_to_scan = [
            os.path.join(self.components_dir, "counterfactual", "CounterfactualLabPanel.js"),
            os.path.join(self.components_dir, "response", "ResponseIntelligencePanel.js")
        ]

        # Regex matching static HR CI patterns like "0.67 [0.44 - 0.98]" in HTML template strings
        hr_ci_pattern = re.compile(r'>\s*0\.\d{2}\s*\[0\.\d{2}\s*-\s*0\.\d{2}\]\s*<')

        for file_path in components_to_scan:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            matches = hr_ci_pattern.findall(content)
            self.assertEqual(
                len(matches), 0,
                f"Found hardcoded HR CI pattern in {file_path}: {matches}"
            )


if __name__ == '__main__':
    unittest.main()
