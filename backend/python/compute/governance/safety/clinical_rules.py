"""
Clinical Rules Module for PERSEPHONE Governance Platform.
Implements configurable, version-controlled organ clearance boundaries backed by
authoritative clinical sources (KDIGO 2024, CTCAE v5.0, FDA Prescribing Labels).
"""
from typing import Dict, List, Any, Optional
import hashlib


# Authoritative versioned clinical boundary standards
ORGAN_RULE_STANDARDS = {
    "RENAL_CLEARANCE_STANDARD": {
        "standard_id": "STD-RENAL-2024.1",
        "authority": "KDIGO 2024 Clinical Practice Guideline / FDA Labeling",
        "version": "2024.1",
        "effective_date": "2024-01-01",
        "rules": {
            "severe_renal_impairment_cutoff": {
                "metric": "eGFR",
                "units": "mL/min/1.73m2",
                "contraindication_threshold": 30.0,
                "dose_reduction_threshold": 50.0,
                "rationale": "Severe renal impairment (eGFR < 30) risks catastrophic accumulation of platinum and renally cleared antineoplastics."
            }
        }
    },
    "HEPATIC_CLEARANCE_STANDARD": {
        "standard_id": "STD-HEPATIC-2023.2",
        "authority": "CTCAE v5.0 / ASCO Hepatic Impairment Criteria",
        "version": "2023.2",
        "effective_date": "2023-06-01",
        "rules": {
            "ast_alt_threshold_normal": {
                "metric": "AST_ALT_xULN",
                "units": "xULN",
                "threshold": 3.0,
                "rationale": "Transaminases > 3x Upper Limit of Normal indicates Grade 2+ hepatotoxicity."
            },
            "ast_alt_threshold_liver_mets": {
                "metric": "AST_ALT_xULN_METS",
                "units": "xULN",
                "threshold": 5.0,
                "rationale": "In presence of documented liver metastases, acceptable baseline ceiling extends to 5x ULN."
            },
            "total_bilirubin_threshold": {
                "metric": "BILIRUBIN_xULN",
                "units": "xULN",
                "threshold": 1.5,
                "rationale": "Total bilirubin > 1.5x ULN indicates impaired hepatic excretion; dose reduction required."
            }
        }
    },
    "HEMATOLOGIC_STANDARD": {
        "standard_id": "STD-HEM-2024.1",
        "authority": "NCCN Task Force on Chemotherapy Safety / CTCAE v5.0",
        "version": "2024.1",
        "effective_date": "2024-01-01",
        "rules": {
            "anc_cutoff": {
                "metric": "ANC",
                "units": "/uL",
                "threshold": 1000.0,
                "rationale": "ANC < 1,000/uL represents Grade 3 neutropenia; cytotoxic and PARPi therapy must be withheld."
            },
            "platelet_cutoff": {
                "metric": "PLATELETS",
                "units": "/uL",
                "threshold": 75000.0,
                "rationale": "Platelet count < 75,000/uL poses unacceptable bleeding risk under cytotoxic or myelosuppressive regimens."
            }
        }
    },
    "CARDIAC_QT_STANDARD": {
        "standard_id": "STD-CARD-2023.1",
        "authority": "ICH E14 Clinical Evaluation of QT/QTc / AHA Guidelines",
        "version": "2023.1",
        "effective_date": "2023-01-01",
        "rules": {
            "qtc_female_cutoff": {"threshold": 470.0, "units": "ms"},
            "qtc_male_cutoff": {"threshold": 450.0, "units": "ms"},
            "qtc_critical_cutoff": {"threshold": 500.0, "units": "ms", "rationale": "QTc > 500 ms poses extreme Torsades de Pointes risk; withhold all QT-prolonging targeted therapies."}
        }
    }
}


class ClinicalRulesEvaluator:
    """
    Evaluates patient organ clearances and hematologic parameters against versioned clinical standards.
    """

    @classmethod
    def evaluate_organ_clearances(
        cls,
        patient_metrics: Dict[str, Any],
        proposed_drug: str = "Olaparib",
        standards_version: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Deterministically evaluates patient parameters against versioned safety thresholds.
        """
        violations = []
        cautions = []
        rule_versions_applied = []

        # 1. Renal Evaluation
        renal_std = ORGAN_RULE_STANDARDS["RENAL_CLEARANCE_STANDARD"]
        rule_versions_applied.append(f"{renal_std['standard_id']}:v{renal_std['version']}")
        egfr = patient_metrics.get("eGFR") or patient_metrics.get("egfr") or patient_metrics.get("renal_eGFR", 85.0)
        try:
            egfr_val = float(egfr)
        except (ValueError, TypeError):
            egfr_val = 85.0

        if egfr_val < renal_std["rules"]["severe_renal_impairment_cutoff"]["contraindication_threshold"]:
            violations.append({
                "organ_system": "RENAL",
                "severity": "CRITICAL",
                "metric": "eGFR",
                "observed_value": egfr_val,
                "threshold": 30.0,
                "units": "mL/min/1.73m2",
                "action": "CONTRAINDICATED",
                "rationale": renal_std["rules"]["severe_renal_impairment_cutoff"]["rationale"],
                "source_ref": f"{renal_std['authority']} ({renal_std['version']})"
            })
        elif egfr_val < renal_std["rules"]["severe_renal_impairment_cutoff"]["dose_reduction_threshold"]:
            cautions.append({
                "organ_system": "RENAL",
                "severity": "MODERATE",
                "metric": "eGFR",
                "observed_value": egfr_val,
                "threshold": 50.0,
                "units": "mL/min/1.73m2",
                "action": "DOSE_REDUCTION_RECOMMENDED",
                "rationale": "Moderate renal impairment (eGFR 30-50); 25-50% dose reduction indicated.",
                "source_ref": f"{renal_std['authority']} ({renal_std['version']})"
            })

        # 2. Hepatic Evaluation
        hep_std = ORGAN_RULE_STANDARDS["HEPATIC_CLEARANCE_STANDARD"]
        rule_versions_applied.append(f"{hep_std['standard_id']}:v{hep_std['version']}")
        ast_alt_xuln = float(patient_metrics.get("AST_ALT_xULN", patient_metrics.get("alt_xuln", 1.0)))
        has_liver_mets = bool(patient_metrics.get("liver_metastases", False))
        ceiling = 5.0 if has_liver_mets else 3.0

        if ast_alt_xuln > ceiling:
            violations.append({
                "organ_system": "HEPATIC",
                "severity": "HIGH",
                "metric": "Transaminases (AST/ALT)",
                "observed_value": ast_alt_xuln,
                "threshold": ceiling,
                "units": "xULN",
                "action": "HOLD_THERAPY",
                "rationale": f"Transaminases {ast_alt_xuln:.1f}x ULN exceed clinical safety threshold of {ceiling}x ULN.",
                "source_ref": f"{hep_std['authority']} ({hep_std['version']})"
            })

        bilirubin_xuln = float(patient_metrics.get("bilirubin_xULN", patient_metrics.get("bili_xuln", 0.8)))
        if bilirubin_xuln > 1.5:
            cautions.append({
                "organ_system": "HEPATIC",
                "severity": "MODERATE",
                "metric": "Total Bilirubin",
                "observed_value": bilirubin_xuln,
                "threshold": 1.5,
                "units": "xULN",
                "action": "DOSE_REDUCTION_RECOMMENDED",
                "rationale": "Bilirubin > 1.5x ULN indicates impaired hepatic clearance.",
                "source_ref": f"{hep_std['authority']} ({hep_std['version']})"
            })

        # 3. Hematologic Evaluation
        hem_std = ORGAN_RULE_STANDARDS["HEMATOLOGIC_STANDARD"]
        rule_versions_applied.append(f"{hem_std['standard_id']}:v{hem_std['version']}")
        anc = float(patient_metrics.get("ANC", patient_metrics.get("anc", 2200.0)))
        platelets = float(patient_metrics.get("platelets", patient_metrics.get("plt", 240000.0)))

        if anc < 1000.0:
            violations.append({
                "organ_system": "HEMATOLOGIC",
                "severity": "CRITICAL",
                "metric": "Absolute Neutrophil Count (ANC)",
                "observed_value": anc,
                "threshold": 1000.0,
                "units": "/uL",
                "action": "WITHHOLD_UNTIL_RECOVERY",
                "rationale": hem_std["rules"]["anc_cutoff"]["rationale"],
                "source_ref": f"{hem_std['authority']} ({hem_std['version']})"
            })
        if platelets < 75000.0:
            violations.append({
                "organ_system": "HEMATOLOGIC",
                "severity": "HIGH",
                "metric": "Platelet Count",
                "observed_value": platelets,
                "threshold": 75000.0,
                "units": "/uL",
                "action": "WITHHOLD_UNTIL_RECOVERY",
                "rationale": hem_std["rules"]["platelet_cutoff"]["rationale"],
                "source_ref": f"{hem_std['authority']} ({hem_std['version']})"
            })

        # 4. Cardiac QTc Evaluation
        card_std = ORGAN_RULE_STANDARDS["CARDIAC_QT_STANDARD"]
        rule_versions_applied.append(f"{card_std['standard_id']}:v{card_std['version']}")
        qtc = float(patient_metrics.get("QTc", patient_metrics.get("qtc", 420.0)))
        gender = str(patient_metrics.get("gender", "FEMALE")).upper()
        qtc_threshold = 470.0 if "FEMALE" in gender else 450.0

        if qtc >= 500.0:
            violations.append({
                "organ_system": "CARDIAC",
                "severity": "CRITICAL",
                "metric": "QTc Interval",
                "observed_value": qtc,
                "threshold": 500.0,
                "units": "ms",
                "action": "IMMEDIATE_CARDIOLOGY_ESCALATION",
                "rationale": card_std["rules"]["qtc_critical_cutoff"]["rationale"],
                "source_ref": f"{card_std['authority']} ({card_std['version']})"
            })
        elif qtc > qtc_threshold:
            cautions.append({
                "organ_system": "CARDIAC",
                "severity": "MODERATE",
                "metric": "QTc Interval",
                "observed_value": qtc,
                "threshold": qtc_threshold,
                "units": "ms",
                "action": "ELECTROLYTE_CHECK_AND_ECG_MONITORING",
                "rationale": f"Prolonged QTc ({qtc} ms > baseline threshold {qtc_threshold} ms).",
                "source_ref": f"{card_std['authority']} ({card_std['version']})"
            })

        passed_all = len(violations) == 0
        status = "PASSED" if passed_all and len(cautions) == 0 else ("CAUTION" if passed_all else "FAILED")

        return {
            "status": status,
            "passed_safety_thresholds": passed_all,
            "critical_violations_count": len(violations),
            "cautions_count": len(cautions),
            "violations": violations,
            "cautions": cautions,
            "rule_versions_applied": rule_versions_applied,
            "evaluated_metrics": {
                "eGFR": egfr_val,
                "AST_ALT_xULN": ast_alt_xuln,
                "bilirubin_xULN": bilirubin_xuln,
                "ANC": anc,
                "platelets": platelets,
                "QTc": qtc
            }
        }
