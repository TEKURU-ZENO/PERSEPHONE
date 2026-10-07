"""
Alerts module for PERSEPHONE Clinical Monitoring & Longitudinal Intelligence.
Generates rule-based prioritized clinical alerts across progression, toxicity,
biomarker rebounds, and treatment delays.
"""

class ClinicalAlertGenerator:
    """
    Evaluates multi-modal longitudinal state and issues categorized clinical alerts.
    """

    @classmethod
    def generate_alerts(cls, trajectory, response, toxicity, biomarkers, progression):
        """
        Synthesizes state into prioritized alerts: CRITICAL, WARNING, INFO.
        """
        alerts = []
        alert_id = 1

        # 1. Progression Alerts
        if progression.get("hasRadiologicProgression"):
            alerts.append({
                "id": f"ALT-{alert_id:03d}",
                "severity": "CRITICAL",
                "category": "progression",
                "title": "Confirmed Disease Progression (RECIST 1.1 PD)",
                "message": f"Tumor volume rebounded by {trajectory.get('reboundPercentFromNadir', 0)}% from nadir. Current velocity: {trajectory.get('currentVelocity')} cm³/day.",
                "actionableRecommendation": "Trigger multidisciplinary tumor board review for Line 2 switch or Phase I/II clinical trial enrollment."
            })
            alert_id += 1
        elif progression.get("hasMolecularRelapse"):
            alerts.append({
                "id": f"ALT-{alert_id:03d}",
                "severity": "WARNING",
                "category": "progression",
                "title": "Molecular Recurrence Lead-Time Warning",
                "message": f"ctDNA VAF elevated to {biomarkers.get('ctdnaVaf', {}).get('current')}% prior to CT manifestation. Lead time estimated at {progression.get('leadTimeDays', 65)} days.",
                "actionableRecommendation": "Schedule early high-resolution contrast CT scan and repeat liquid biopsy."
            })
            alert_id += 1

        # 2. Toxicity Alerts
        if toxicity.get("hasSevereToxicity"):
            alerts.append({
                "id": f"ALT-{alert_id:03d}",
                "severity": "CRITICAL",
                "category": "toxicity",
                "title": "Severe Adverse Event (CTCAE Grade >= 3)",
                "message": f"Dose-limiting toxicity observed. Cumulative toxicity index: {toxicity.get('cumulativeToxicityScore')}/10.",
                "actionableRecommendation": "Implement dose interruption or 20% dose reduction per institutional protocol."
            })
            alert_id += 1
        elif toxicity.get("currentGrade", 0) >= 2:
            alerts.append({
                "id": f"ALT-{alert_id:03d}",
                "severity": "WARNING",
                "category": "toxicity",
                "title": "Moderate Toxicity Burden (Grade 2)",
                "message": f"Active Grade 2 toxicity reported (fatigue/anemia). Monitor organ function.",
                "actionableRecommendation": "Supportive care optimization and CBC/CMP monitoring within 7 days."
            })
            alert_id += 1

        # 3. Biomarker Alerts
        ca125_info = biomarkers.get("ca125", {})
        if ca125_info.get("isElevated") and ca125_info.get("velocity", 0) > 0.5:
            alerts.append({
                "id": f"ALT-{alert_id:03d}",
                "severity": "WARNING",
                "category": "biomarker",
                "title": "Rapid CA-125 Biomarker Acceleration",
                "message": f"Serum CA-125 rising at velocity of +{ca125_info.get('velocity')} U/mL/day (current: {ca125_info.get('current')} U/mL).",
                "actionableRecommendation": "Correlate with pelvic examination and cross-sectional imaging."
            })
            alert_id += 1

        # 4. Response Info Alert
        if response.get("isResponding"):
            alerts.append({
                "id": f"ALT-{alert_id:03d}",
                "severity": "INFO",
                "category": "response",
                "title": f"Objective Response Confirmed ({response.get('bestOverallResponse')})",
                "message": f"Maximum depth of response: {response.get('depthOfResponsePercent')}% reduction from baseline.",
                "actionableRecommendation": "Maintain current maintenance regimen; next scheduled scan in 12 weeks."
            })
            alert_id += 1

        # Sort: CRITICAL first, then WARNING, then INFO
        severity_order = {"CRITICAL": 0, "WARNING": 1, "INFO": 2}
        alerts.sort(key=lambda x: severity_order.get(x["severity"], 3))

        return alerts
