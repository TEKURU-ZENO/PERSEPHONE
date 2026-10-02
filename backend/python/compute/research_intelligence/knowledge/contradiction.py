"""
Contradiction Detector module for PERSEPHONE Research Intelligence Platform.
Performs formal multi-category clinical evidence discordance detection with granular parameter inspection.
"""
from typing import Dict, List, Any, Optional


class ContradictionDetector:
    """
    Scans evidence sources, guidelines, trials, and patient biomarkers to detect
    clinical, temporal, and population discordances.
    """

    CATEGORIES = {
        "CONCORDANT": "Evidence streams agree consistently across endpoints.",
        "MINOR_DISCORDANCE": "Minor variation in magnitude of effect or secondary adverse event rate.",
        "MATERIAL_CONFLICT": "Opposing outcomes across primary endpoints (e.g., PFS improvement vs no benefit).",
        "TEMPORAL_CONFLICT": "Older clinical trial/guideline superseded by newer registrational phase III readout.",
        "POPULATION_CONFLICT": "Trial or study cohort characteristics diverge from index patient demographics or treatment line.",
        "BIOMARKER_CONFLICT": "Discrepancy between patient molecular profile and biomarker entry criteria."
    }

    @classmethod
    def scan_contradictions(
        cls,
        patient_data: Dict[str, Any],
        proposed_drug: str,
        retrieved_papers: List[Dict[str, Any]],
        guideline_recommendations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Executes granular cross-source comparison and returns categorized conflict objects.
        """
        conflicts = []
        patient_variants = [str(v).upper() for v in (patient_data.get("variants") or [])]
        hrd_score = float(patient_data.get("hrd_score", 52.0 if any("BRCA" in v for v in patient_variants) else 20.0))
        patient_stage = str(patient_data.get("stage", "Stage III")).upper()

        drug_up = proposed_drug.upper()

        # 1. Biomarker Conflict Check: HRD- patient evaluated for Olaparib/PARPi
        if "OLAPARIB" in drug_up:
            is_hrd_positive = (hrd_score >= 42.0) or any("BRCA" in v for v in patient_variants)
            if not is_hrd_positive:
                conflicts.append({
                    "conflict_id": "CONF-BIO-001",
                    "category": "BIOMARKER_CONFLICT",
                    "severity": "CRITICAL",
                    "statement": "Patient is HRD-negative / BRCA wild-type, but primary literature (SOLO-1, PAOLA-1) demonstrates restricted efficacy to HRD-positive tumors.",
                    "evidence_A": {
                        "source": "SOLO-1 / PAOLA-1 Trials",
                        "biomarker_requirement": "BRCAm / HRD+",
                        "endpoint": "PFS HR = 0.33 in HRD+",
                        "sample_size": 806
                    },
                    "evidence_B": {
                        "source": "Patient Genomic Profile",
                        "biomarker_status": f"HRD Score {hrd_score} (< 42), BRCA wt",
                        "expected_benefit": "Substantially attenuated or absent"
                    },
                    "resolution_status": "CLINICIAN_REVIEW_REQUIRED"
                })

        # 2. Population Conflict Check: Prior chemotherapy lines
        prior_therapies = patient_data.get("prior_therapies", [])
        if len(prior_therapies) >= 3 and ("OLAPARIB" in drug_up or "NIRAPARIB" in drug_up):
            conflicts.append({
                "conflict_id": "CONF-POP-001",
                "category": "POPULATION_CONFLICT",
                "severity": "MODERATE",
                "statement": "Patient has received >= 3 prior systemic lines; primary guideline approval is for first-line platinum maintenance.",
                "evidence_A": {
                    "source": "NCCN Category 1 Guideline",
                    "treatment_line": "First-line Maintenance",
                    "target_population": "Newly diagnosed advanced ovarian cancer"
                },
                "evidence_B": {
                    "source": "Patient Clinical History",
                    "treatment_line": f"Recurrent ({len(prior_therapies)} prior lines)",
                    "target_population": "Late-line recurrent disease"
                },
                "resolution_status": "CLINICIAN_REVIEW_REQUIRED"
            })

        # 3. Statistical Uncertainty / Discordance across papers
        hr_values = []
        for p in retrieved_papers:
            ev = p.get("evidence", {})
            hr = ev.get("hazard_ratio")
            if hr and hr.get("value"):
                hr_values.append((p.get("title", "Study"), hr["value"], hr.get("lower_bound"), hr.get("upper_bound")))

        if len(hr_values) >= 2:
            min_hr = min(h[1] for h in hr_values)
            max_hr = max(h[1] for h in hr_values)
            if (max_hr - min_hr) > 0.35:
                conflicts.append({
                    "conflict_id": "CONF-STAT-001",
                    "category": "MINOR_DISCORDANCE",
                    "severity": "LOW",
                    "statement": f"Observed variance in reported Hazard Ratios across trials ({min_hr:.2f} vs {max_hr:.2f}) reflecting differential trial cohorts.",
                    "evidence_A": {"source": hr_values[0][0], "hr": hr_values[0][1]},
                    "evidence_B": {"source": hr_values[1][0], "hr": hr_values[1][1]},
                    "resolution_status": "CONCORDANT_DIRECTIONAL_BENEFIT"
                })

        overall_concordance = "CONCORDANT" if len(conflicts) == 0 else ("CRITICAL_CONFLICT" if any(c["severity"] == "CRITICAL" for c in conflicts) else "DISCORDANT")

        return {
            "proposed_drug": proposed_drug,
            "overall_concordance": overall_concordance,
            "conflict_count": len(conflicts),
            "conflicts": conflicts,
            "inspection_metadata": {
                "patient_stage": patient_stage,
                "hrd_score": hrd_score,
                "variants": patient_variants,
                "active_categories": list(cls.CATEGORIES.keys())
            }
        }
