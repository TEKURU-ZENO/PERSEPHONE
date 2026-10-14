"""
backend/python/tests/scientific/test_safety_gate.py

Scientific Unit Tests for Deterministic Clinical Safety Gate (Task C2).
Verifies:
- Rule 1: Genetic contraindications (PARP in HR-proficient, Anti-EGFR in KRAS CRC,
  platinum in anaphylaxis, DPYD deficiency, BRAF-wt).
- Rule 2: Supratherapeutic dose ceiling enforcement.
- Rule 3: Off-label & investigational Phase 1 oncologist override requirement.
- Standard-of-care safe substitutions and confidence zeroing.
"""

import sys
from pathlib import Path
import pytest

ROOT_DIR = Path(__file__).resolve().parents[4]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.python.compute.clinical_evidence.schemas import (
    EvidenceLevel,
    EvidenceRecommendation,
    PatientClinicalProfile,
)
from backend.python.compute.clinical_evidence.safety_gate import (
    DeterministicSafetyGate,
    FDA_DOSE_MAXIMA,
    SOC_SUBSTITUTIONS,
)


def test_rule_1a_blocks_parp_in_hr_proficient_ovarian():
    """Rule 1A: PARP inhibitor must be blocked in BRCA/HR-proficient tumors."""
    profile = PatientClinicalProfile(
        patient_id="PT-SAFE-01",
        cancer_type="High-Grade Serous Ovarian Cancer",
        stage="Stage IVB",
        somatic_mutations=["TP53 R273H"],  # No BRCA / HRD
    )
    rec = EvidenceRecommendation(
        recommendation="Olaparib maintenance monotherapy (300 mg BID orally)",
        rationale="PARP inhibitor maintenance.",
        evidence_level=EvidenceLevel.LEVEL_1A,
        confidence=0.90,
    )

    gated = DeterministicSafetyGate.apply_safety_gate(profile, rec)
    assert not gated.safety_gate_passed
    assert gated.confidence == 0.0
    assert "BLOCKED:" in gated.recommendation
    assert "Paclitaxel + Carboplatin + Bevacizumab" in gated.recommendation
    assert any("C2.2 VIOLATION" in v or "PARP inhibitor" in v for v in gated.safety_violations)


def test_rule_1b_blocks_anti_egfr_in_kras_mutant_crc():
    """Rule 1B: Anti-EGFR therapies must be blocked in KRAS-mutant colorectal cancer."""
    profile = PatientClinicalProfile(
        patient_id="PT-SAFE-02",
        cancer_type="Colorectal Cancer",
        stage="Stage IV",
        somatic_mutations=["KRAS G12D", "TP53 R248W"],
    )
    rec = EvidenceRecommendation(
        recommendation="Cetuximab monotherapy (500 mg/m² q2w)",
        rationale="Anti-EGFR therapy for mCRC.",
        evidence_level=EvidenceLevel.LEVEL_1A,
        confidence=0.85,
    )

    gated = DeterministicSafetyGate.apply_safety_gate(profile, rec)
    assert not gated.safety_gate_passed
    assert gated.confidence == 0.0
    assert "BLOCKED:" in gated.recommendation
    assert "FOLFIRI + Bevacizumab" in gated.recommendation
    assert any("KRAS/NRAS-mutant" in v for v in gated.safety_violations)


def test_rule_1c_blocks_platinum_rechallenge_in_anaphylaxis():
    """Rule 1C: Platinum agents must be blocked in documented platinum anaphylaxis."""
    profile = PatientClinicalProfile(
        patient_id="PT-SAFE-03",
        cancer_type="High-Grade Serous Ovarian Cancer",
        stage="Stage IIIC",
        somatic_mutations=["TP53 Y220C"],
        allergies_hypersensitivities=["Carboplatin (Grade 4 anaphylactic shock)", "Platinum allergy"],
    )
    rec = EvidenceRecommendation(
        recommendation="Carboplatin (AUC 5) + Paclitaxel (175 mg/m²)",
        rationale="Platinum rechallenge.",
        evidence_level=EvidenceLevel.LEVEL_1A,
        confidence=0.88,
    )

    gated = DeterministicSafetyGate.apply_safety_gate(profile, rec)
    assert not gated.safety_gate_passed
    assert gated.confidence == 0.0
    assert "BLOCKED:" in gated.recommendation
    assert "Paclitaxel + Gemcitabine" in gated.recommendation
    assert any("platinum hypersensitivity" in v.lower() for v in gated.safety_violations)


def test_rule_1d_blocks_fluoropyrimidines_in_dpyd_deficiency():
    """Rule 1D: Fluoropyrimidines must be blocked in DPYD deficiency."""
    profile = PatientClinicalProfile(
        patient_id="PT-SAFE-04",
        cancer_type="Colorectal Cancer",
        stage="Stage III",
        somatic_mutations=["APC mutation"],
        germline_variants=["DPYD*2A"],
        allergies_hypersensitivities=["DPYD deficiency"],
    )
    rec = EvidenceRecommendation(
        recommendation="Capecitabine adjuvant monotherapy (1250 mg/m² BID)",
        rationale="Adjuvant capecitabine.",
        evidence_level=EvidenceLevel.LEVEL_1A,
        confidence=0.85,
    )

    gated = DeterministicSafetyGate.apply_safety_gate(profile, rec)
    assert not gated.safety_gate_passed
    assert "BLOCKED:" in gated.recommendation
    assert "Irinotecan + Oxaliplatin" in gated.recommendation
    assert any("DPYD deficiency" in v for v in gated.safety_violations)


def test_rule_1e_blocks_braf_inhibitors_in_braf_wt():
    """Rule 1E: BRAF inhibitors must be blocked in BRAF-wildtype tumors."""
    profile = PatientClinicalProfile(
        patient_id="PT-SAFE-05",
        cancer_type="Melanoma",
        stage="Stage IV",
        somatic_mutations=["NRAS Q61R"],  # BRAF wildtype
    )
    rec = EvidenceRecommendation(
        recommendation="Dabrafenib (150 mg BID) + Trametinib (2 mg daily)",
        rationale="Targeted kinase therapy.",
        evidence_level=EvidenceLevel.LEVEL_1A,
        confidence=0.80,
    )

    gated = DeterministicSafetyGate.apply_safety_gate(profile, rec)
    assert not gated.safety_gate_passed
    assert "BLOCKED:" in gated.recommendation
    assert "Nivolumab + Ipilimumab" in gated.recommendation
    assert any("BRAF-wildtype" in v for v in gated.safety_violations)


def test_rule_2_blocks_supratherapeutic_dose_limits():
    """Rule 2: Doses exceeding FDA label maxima must be intercepted."""
    profile = PatientClinicalProfile(
        patient_id="PT-SAFE-06",
        cancer_type="Non-Small Cell Lung Cancer",
        stage="Stage IV",
        somatic_mutations=["EGFR L858R"],
    )
    # Osimertinib ceiling is 80 mg daily. 160 mg is supratherapeutic.
    rec = EvidenceRecommendation(
        recommendation="Osimertinib 160 mg once daily orally",
        rationale="Escalated dose EGFR TKI.",
        evidence_level=EvidenceLevel.LEVEL_1A,
        confidence=0.90,
    )

    gated = DeterministicSafetyGate.apply_safety_gate(profile, rec)
    assert not gated.safety_gate_passed
    assert any("C2.5 VIOLATION" in v or "Supratherapeutic" in v for v in gated.safety_violations)
    assert "80 mg" in gated.recommendation


def test_rule_3_flags_phase_1_investigational_override():
    """Rule 3: Phase 1 investigational protocols require mandatory oncologist override."""
    profile = PatientClinicalProfile(
        patient_id="PT-SAFE-07",
        cancer_type="High-Grade Serous Ovarian Cancer",
        stage="Stage IV",
        somatic_mutations=["EGFR amplification"],
    )
    rec = EvidenceRecommendation(
        recommendation="Phase 1 investigational trial of osimertinib + experimental ATR inhibitor",
        rationale="Investigational dose escalation.",
        evidence_level=EvidenceLevel.LEVEL_3,
        confidence=0.50,
    )

    gated = DeterministicSafetyGate.apply_safety_gate(profile, rec)
    assert gated.requires_oncologist_override
    assert gated.override_reason is not None
    assert "Phase 1" in gated.override_reason or "Investigational" in gated.override_reason
