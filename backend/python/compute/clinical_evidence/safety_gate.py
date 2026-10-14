"""
backend/python/compute/clinical_evidence/safety_gate.py

Deterministic Clinical Safety Gate (Task C2).
Enforces hard-coded clinical safety rules after LLM inference.
Rejects the output if any of these fail:
1. Every cited NCT ID is in verified_trials.json
2. Every recommended drug targets an alteration the patient actually has (drug-target allowlist)
3. No drug the patient already failed is recommended again
4. Absolute genetic, hypersensitivity, and pharmacogenomic contraindications
5. FDA label maximum dose ceilings

If the gate rejects, the agent abstains with a reason code.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set

from backend.python.compute.clinical_evidence.schemas import (
    EvidenceLevel,
    EvidenceRecommendation,
    PatientClinicalProfile,
    SafetyCheckResult,
)

ROOT_DIR = Path(__file__).resolve().parents[4]
VERIFIED_TRIALS_PATH = ROOT_DIR / "datasets" / "knowledge" / "verified_trials.json"

# Standard of Care substitutions when contraindications are blocked
SOC_SUBSTITUTIONS = {
    "anti_egr_kras_crc": "FOLFIRI + Bevacizumab (VEGF-targeted standard for KRAS-mutant mCRC)",
    "parp_hr_proficient": "Paclitaxel + Carboplatin + Bevacizumab (Anti-angiogenic standard for HR-proficient ovarian)",
    "platinum_hypersensitivity": "Paclitaxel + Gemcitabine (Non-platinum cytotoxic doublet)",
    "braf_wt_melanoma": "Nivolumab + Ipilimumab (First-line dual checkpoint inhibition for BRAF-wt)",
    "dpyd_deficiency": "Irinotecan + Oxaliplatin (Non-fluoropyrimidine alternative)",
    "failed_osimertinib": "Amivantamab + Chemotherapy (Standard post-osimertinib progression regimen)",
    "kras_g12d_mismatch": "FOLFIRI + Bevacizumab (Chemotherapy + VEGF standard for non-G12C KRAS)",
    "mss_crc_io_mismatch": "FOLFOX + Bevacizumab (Standard cytotoxic doublet for MSS mCRC)",
}

# FDA Label Maximum Dose Ceilings
FDA_DOSE_MAXIMA = {
    "olaparib": {"max_daily_mg": 600.0, "unit": "mg/day (300 mg BID)"},
    "rucaparib": {"max_daily_mg": 1200.0, "unit": "mg/day (600 mg BID)"},
    "niraparib": {"max_daily_mg": 300.0, "unit": "mg/day once daily"},
    "osimertinib": {"max_daily_mg": 80.0, "unit": "mg/day once daily"},
    "sotorasib": {"max_daily_mg": 960.0, "unit": "mg/day once daily"},
    "adagrasib": {"max_daily_mg": 1200.0, "unit": "mg/day (600 mg BID)"},
    "erlotinib": {"max_daily_mg": 150.0, "unit": "mg/day once daily"},
    "gefitinib": {"max_daily_mg": 250.0, "unit": "mg/day once daily"},
    "afatinib": {"max_daily_mg": 40.0, "unit": "mg/day once daily"},
}


class DeterministicSafetyGate:
    """
    Hard-coded clinical governance gate enforcing non-negotiable patient safety rules.
    """

    _verified_nct_cache: Optional[Set[str]] = None

    @classmethod
    def _get_verified_nct_ids(cls) -> Set[str]:
        if cls._verified_nct_cache is not None:
            return cls._verified_nct_cache
        if VERIFIED_TRIALS_PATH.exists():
            with open(VERIFIED_TRIALS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                cls._verified_nct_cache = set(data.get("verified", {}).keys())
        else:
            cls._verified_nct_cache = set()
        return cls._verified_nct_cache

    @classmethod
    def evaluate(
        cls,
        profile: PatientClinicalProfile,
        recommendation: EvidenceRecommendation,
    ) -> SafetyCheckResult:
        violations: List[str] = []
        reason_codes: List[str] = []
        requires_override = False
        override_reasons: List[str] = []
        substitute_rec: Optional[str] = None

        recommendation_text = recommendation.recommendation or ""
        rec_lower = recommendation_text.lower()
        all_mutations_str = " ".join(profile.somatic_mutations + profile.germline_variants).upper()
        cancer_type_lower = profile.cancer_type.lower()
        allergies_str = " ".join(profile.allergies_hypersensitivities).lower()

        # =====================================================================
        # RULE C2.1: VERIFIED CLINICAL TRIALS REGISTRY CHECK
        # Every cited NCT ID must exist in verified_trials.json
        # =====================================================================
        verified_trials = cls._get_verified_nct_ids()
        cited_ncts = set(recommendation.cited_trial_ids)
        for cit in recommendation.citations:
            if cit.nct_id:
                cited_ncts.add(cit.nct_id)
        text_ncts = set(re.findall(r"NCT\d{8}", recommendation_text))
        all_ncts = cited_ncts.union(text_ncts)

        for nct in all_ncts:
            if nct not in verified_trials:
                violations.append(
                    f"C2.1 VIOLATION: Unverified clinical trial identifier {nct} cited. "
                    f"All trials must be documented and verified in datasets/knowledge/verified_trials.json."
                )
                reason_codes.append("REJECTED_UNVERIFIED_TRIAL")

        # =====================================================================
        # RULE C2.2: DRUG-TARGET ALLOWLIST CHECK
        # Every recommended targeted drug must target an alteration the patient actually has
        # =====================================================================

        # 2.2A. KRAS G12C inhibitors (Sotorasib / Adagrasib)
        if any(d in rec_lower for d in ["sotorasib", "adagrasib"]):
            has_g12c = ("KRAS" in all_mutations_str and "G12C" in all_mutations_str)
            if not has_g12c:
                violations.append(
                    "C2.2 VIOLATION: KRAS G12C inhibitor recommended in tumor lacking KRAS G12C mutation "
                    "(e.g. KRAS G12D or KRAS wild-type). Sotorasib/adagrasib covalently bind the mutated Cys-12 residue only."
                )
                reason_codes.append("REJECTED_TARGET_MISMATCH")
                substitute_rec = SOC_SUBSTITUTIONS["kras_g12d_mismatch"]

        # 2.2B. EGFR TKIs (Osimertinib / Erlotinib / Gefitinib)
        if any(d in rec_lower for d in ["osimertinib", "erlotinib", "gefitinib"]):
            has_egfr = any(mut in all_mutations_str for mut in ["EGFR", "L858R", "EXON 19", "T790M", "E746_A750DEL"])
            if not has_egfr and any(t in cancer_type_lower for t in ["lung", "nsclc"]):
                violations.append(
                    "C2.2 VIOLATION: EGFR TKI recommended in EGFR wild-type NSCLC."
                )
                reason_codes.append("REJECTED_TARGET_MISMATCH")

        # 2.2C. PARP Inhibitors (Olaparib / Niraparib / Rucaparib)
        parp_drugs = ["olaparib", "rucaparib", "niraparib", "talazoparib"]
        if any(drug in rec_lower for drug in parp_drugs):
            hrd_genes = ["BRCA1", "BRCA2", "PALB2", "RAD51C", "RAD51D", "ATM", "CDK12", "BARD1", "BRIP1", "HRD+"]
            has_hrd = any(gene in all_mutations_str for gene in hrd_genes)
            if not has_hrd:
                violations.append(
                    "C2.2 VIOLATION: PARP inhibitor recommended in HR-proficient / BRCA-wildtype tumor "
                    "lacking homologous recombination deficiency or DNA repair defect (ASCO/NCCN biomarker mismatch)."
                )
                reason_codes.append("REJECTED_TARGET_MISMATCH")
                substitute_rec = SOC_SUBSTITUTIONS["parp_hr_proficient"]

        # 2.2D. Anti-EGFR mAb in Colorectal Cancer (Cetuximab / Panitumumab)
        egfr_mabs = ["cetuximab", "panitumumab"]
        is_egfr_mab = any(drug in rec_lower for drug in egfr_mabs)
        is_crc = any(term in cancer_type_lower for term in ["colorectal", "colon", "rectal", "crc"])
        if is_egfr_mab and is_crc:
            has_ras_mutation = ("KRAS" in all_mutations_str or "NRAS" in all_mutations_str)
            if has_ras_mutation:
                violations.append(
                    "C2.2 VIOLATION: Anti-EGFR monoclonal antibody (cetuximab/panitumumab) recommended in "
                    "KRAS/NRAS-mutant colorectal cancer. Constitutive downstream MAPK activation confers zero efficacy "
                    "and documented inferior outcomes (FDA black box / NCCN Category 3 contraindication)."
                )
                reason_codes.append("REJECTED_TARGET_MISMATCH")
                substitute_rec = SOC_SUBSTITUTIONS["anti_egr_kras_crc"]

        # 2.2E. BRAF Inhibitors (Dabrafenib / Vemurafenib / Encorafenib)
        braf_inhibitors = ["vemurafenib", "dabrafenib", "encorafenib"]
        if any(drug in rec_lower for drug in braf_inhibitors):
            has_braf_v600 = ("BRAF" in all_mutations_str and ("V600" in all_mutations_str or "V600E" in all_mutations_str or "V600K" in all_mutations_str))
            if not has_braf_v600:
                violations.append(
                    "C2.2 VIOLATION: BRAF inhibitor recommended in BRAF-wildtype malignancy "
                    "(induces paradoxical CRAF dimer activation and accelerated tumor growth)."
                )
                reason_codes.append("REJECTED_TARGET_MISMATCH")
                substitute_rec = SOC_SUBSTITUTIONS["braf_wt_melanoma"]

        # 2.2F. Immunotherapy in Colorectal Cancer (Pembrolizumab / Nivolumab)
        if any(drug in rec_lower for drug in ["pembrolizumab", "nivolumab"]) and is_crc:
            has_msi = any(m in all_mutations_str for m in ["MSI-H", "DMMR"])
            has_mss = ("MSS" in all_mutations_str or "PMMR" in all_mutations_str)
            if has_mss and not has_msi:
                violations.append(
                    "C2.2 VIOLATION: Single-agent immune checkpoint inhibitor proposed for microsatellite-stable (MSS / pMMR) "
                    "colorectal cancer lacking mismatch repair deficiency (NCCN guideline mismatch)."
                )
                reason_codes.append("REJECTED_TARGET_MISMATCH")
                substitute_rec = SOC_SUBSTITUTIONS["mss_crc_io_mismatch"]

        # =====================================================================
        # RULE C2.3: NO FAILED DRUG RECHALLENGE
        # No drug the patient already failed is recommended again as monotherapy
        # =====================================================================
        for therapy in profile.prior_therapies:
            t_lower = therapy.lower()
            if any(term in t_lower for term in ["progression", "resistant", "refractory", "failed", "failure"]):
                for drug_cand in ["osimertinib", "gefitinib", "erlotinib", "alpelisib", "sotorasib", "adagrasib", "olaparib"]:
                    if drug_cand in t_lower and drug_cand in rec_lower:
                        if "+" not in rec_lower or "monotherapy" in rec_lower:
                            violations.append(
                                f"C2.3 VIOLATION: Patient previously progressed/failed on {drug_cand.capitalize()}; "
                                f"re-treatment with the same failed regimen without novel sensitizing combination is contraindicated."
                            )
                            reason_codes.append("REJECTED_FAILED_DRUG_RECHALLENGE")
                            if drug_cand == "osimertinib":
                                substitute_rec = SOC_SUBSTITUTIONS["failed_osimertinib"]

        # =====================================================================
        # RULE C2.4: PHARMACOGENOMIC & HYPERSENSITIVITY CONTRAINDICATIONS
        # =====================================================================

        # Platinum anaphylaxis
        platinum_drugs = ["carboplatin", "cisplatin", "oxaliplatin"]
        if any(drug in rec_lower for drug in platinum_drugs):
            has_plat_allergy = any(term in allergies_str for term in ["platinum", "carboplatin", "cisplatin", "oxaliplatin", "anaphylaxis"])
            if has_plat_allergy:
                violations.append(
                    "C2.4 VIOLATION: Platinum cytotoxic agent recommended in patient with documented "
                    "platinum hypersensitivity / severe allergic reaction history."
                )
                reason_codes.append("REJECTED_HYPERSENSITIVITY_CONTRAINDICATION")
                substitute_rec = SOC_SUBSTITUTIONS["platinum_hypersensitivity"]

        # DPYD deficiency
        fluoropyrimidines = ["5-fu", "fluorouracil", "capecitabine", "folfiri", "folfox", "folfirinox"]
        if any(drug in rec_lower for drug in fluoropyrimidines):
            has_dpyd = ("DPYD" in all_mutations_str or "dpyd" in allergies_str)
            if has_dpyd:
                violations.append(
                    "C2.4 VIOLATION: Fluoropyrimidine regimen recommended in documented DPYD deficiency "
                    "(lethal systemic myelosuppression and mucositis risk)."
                )
                reason_codes.append("REJECTED_PHARMACOGENOMIC_CONTRAINDICATION")
                substitute_rec = SOC_SUBSTITUTIONS["dpyd_deficiency"]

        # =====================================================================
        # RULE C2.5: SUPRATHERAPEUTIC DOSE MAXIMUM CEILINGS
        # =====================================================================
        for drug_name, dose_spec in FDA_DOSE_MAXIMA.items():
            if drug_name in rec_lower:
                dose_pattern = re.compile(rf"{drug_name}.*?(\d{{2,4}})\s*mg", re.IGNORECASE)
                match = dose_pattern.search(recommendation_text)
                if match:
                    parsed_mg = float(match.group(1))
                    if parsed_mg > dose_spec["max_daily_mg"]:
                        violations.append(
                            f"C2.5 VIOLATION: Supratherapeutic dosing detected for {drug_name.capitalize()}. "
                            f"Recommended dose ({parsed_mg:.0f} mg) exceeds FDA label maximum ceiling of "
                            f"{dose_spec['max_daily_mg']:.0f} {dose_spec['unit']}."
                        )
                        reason_codes.append("REJECTED_SUPRATHERAPEUTIC_DOSE")
                        if not substitute_rec:
                            if drug_name == "osimertinib":
                                substitute_rec = "Osimertinib 80 mg once daily orally (FDA label standard dose)"
                            elif drug_name == "olaparib":
                                substitute_rec = "Olaparib 300 mg BID (600 mg/day) (FDA label standard dose)"
                            else:
                                substitute_rec = f"{drug_name.capitalize()} standard dose ({dose_spec['max_daily_mg']:.0f} {dose_spec['unit']})"

        # =====================================================================
        # RULE C2.6: OFF-LABEL & PHASE 1 MANDATED ONCOLOGIST OVERRIDE
        # =====================================================================
        is_phase_1 = any(term in rec_lower for term in ["phase 1", "phase i", "investigational", "first-in-human"])
        if is_phase_1:
            requires_override = True
            override_reasons.append("Investigational Phase 1 clinical trial protocol requires explicit multidisciplinary sign-off.")

        if "osimertinib" in rec_lower and not any(term in cancer_type_lower for term in ["lung", "nsclc"]):
            requires_override = True
            override_reasons.append("Off-label third-generation EGFR TKI application outside of NSCLC indication.")

        passed = len(violations) == 0
        primary_reason_code = reason_codes[0] if reason_codes else None

        return SafetyCheckResult(
            passed=passed,
            violations=violations,
            reason_code=primary_reason_code,
            requires_override=requires_override,
            override_reason=" | ".join(override_reasons) if override_reasons else None,
            substitute_recommendation=substitute_rec,
        )

    @classmethod
    def apply_safety_gate(
        cls,
        profile: PatientClinicalProfile,
        recommendation: EvidenceRecommendation,
    ) -> EvidenceRecommendation:
        """
        Applies deterministic rules to an EvidenceRecommendation, mutating flags,
        setting abstain=True if rejected, and substituting standard-of-care.
        """
        result = cls.evaluate(profile, recommendation)

        if not result.passed:
            recommendation.safety_gate_passed = False
            recommendation.safety_violations = result.violations
            recommendation.contraindications.extend(result.violations)
            recommendation.confidence = 0.0
            recommendation.abstain = True
            recommendation.abstain_reason = result.reason_code or "SAFETY_GATE_REJECTED"

            if result.substitute_recommendation:
                recommendation.rationale = (
                    f"[SAFETY GATE REJECTED ORIGINAL RECOMMENDATION: {recommendation.recommendation}]\n"
                    f"Reason Code: {recommendation.abstain_reason}\n"
                    f"Violations: {'; '.join(result.violations)}\n"
                    f"Substituted Standard of Care: {result.substitute_recommendation}"
                )
                recommendation.recommendation = f"BLOCKED: {result.substitute_recommendation}"
                recommendation.evidence_level = EvidenceLevel.LEVEL_1A
            else:
                recommendation.recommendation = f"ABSTAIN [{recommendation.abstain_reason}]: Review required by multidisciplinary tumor board"
                recommendation.evidence_level = EvidenceLevel.NOT_APPLICABLE
        else:
            recommendation.safety_gate_passed = True
            recommendation.safety_violations = []

        if result.requires_override:
            recommendation.requires_oncologist_override = True
            recommendation.override_reason = result.override_reason
            if "override" not in (recommendation.recommendation or "").lower():
                recommendation.recommendation = (recommendation.recommendation or "") + " (Investigational Phase 1 trial with oncologist override sign-off)"

        return recommendation
