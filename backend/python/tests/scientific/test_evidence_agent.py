"""
backend/python/tests/scientific/test_evidence_agent.py

Scientific Unit Tests for Clinical Evidence Agent (Task C1).
Verifies Pydantic schema validation, deterministic fallback logic,
biomarker alignment, and authentic citation integrity.
"""

import sys
from pathlib import Path
import pytest

ROOT_DIR = Path(__file__).resolve().parents[4]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.python.compute.clinical_evidence.schemas import (
    Citation,
    EvidenceLevel,
    EvidenceRecommendation,
    PatientClinicalProfile,
)
from backend.python.compute.clinical_evidence.evidence_agent import EvidenceAgent


def test_schema_serialization_and_validation():
    """Verifies that schemas enforce data types and serialization boundaries."""
    citation = Citation(
        nct_id="NCT01844986",
        title="SOLO-1 Trial",
        pmid="30345906",
    )
    assert citation.nct_id == "NCT01844986"

    profile = PatientClinicalProfile(
        patient_id="PT-TEST-01",
        cancer_type="High-Grade Serous Ovarian Cancer",
        stage="Stage IIIC",
        somatic_mutations=["BRCA1 c.5266dupC"],
    )
    assert profile.patient_id == "PT-TEST-01"
    assert profile.somatic_mutations == ["BRCA1 c.5266dupC"]

    rec = EvidenceRecommendation(
        recommendation="Olaparib maintenance monotherapy (300 mg BID orally)",
        rationale="Synthetic lethality in homologous recombination deficiency.",
        evidence_level=EvidenceLevel.LEVEL_1A,
        citations=[citation],
        contraindications=[],
        confidence=0.95,
        source="deterministic_fallback",
    )
    dumped = rec.model_dump()
    assert dumped["evidence_level"] == "1A"
    assert dumped["source"] == "deterministic_fallback"
    assert dumped["confidence"] == 0.95


def test_agent_ovarian_brca1_recommendation():
    """Verifies EvidenceAgent produces Level 1A Olaparib for BRCA1 ovarian cancer."""
    agent = EvidenceAgent()
    profile = PatientClinicalProfile(
        patient_id="PT-OV-01",
        cancer_type="High-Grade Serous Ovarian Cancer",
        stage="Stage IIIC",
        somatic_mutations=["BRCA1 c.5266dupC"],
        prior_therapies=["Carboplatin + Paclitaxel"],
    )

    rec = agent.generate_recommendation(profile, enforce_safety_gate=False)
    assert "olaparib" in rec.recommendation.lower()
    assert rec.evidence_level == EvidenceLevel.LEVEL_1A
    assert rec.source == "deterministic_fallback"
    assert any(c.nct_id == "NCT01844986" for c in rec.citations)


def test_agent_nsclc_egfr_recommendation():
    """Verifies EvidenceAgent produces Level 1A Osimertinib for EGFR-mutated NSCLC."""
    agent = EvidenceAgent()
    profile = PatientClinicalProfile(
        patient_id="PT-LUNG-01",
        cancer_type="Non-Small Cell Lung Cancer",
        stage="Stage IVA",
        somatic_mutations=["EGFR L858R"],
    )

    rec = agent.generate_recommendation(profile, enforce_safety_gate=False)
    assert "osimertinib" in rec.recommendation.lower()
    assert rec.evidence_level == EvidenceLevel.LEVEL_1A
    assert any(c.nct_id == "NCT02296125" for c in rec.citations)


def test_agent_nsclc_kras_g12c_recommendation():
    """Verifies EvidenceAgent produces Level 2A Sotorasib for KRAS G12C NSCLC."""
    agent = EvidenceAgent()
    profile = PatientClinicalProfile(
        patient_id="PT-LUNG-02",
        cancer_type="Non-Small Cell Lung Cancer",
        stage="Stage IV",
        somatic_mutations=["KRAS G12C"],
    )

    rec = agent.generate_recommendation(profile, enforce_safety_gate=False)
    assert "sotorasib" in rec.recommendation.lower()
    assert rec.evidence_level == EvidenceLevel.LEVEL_2A
    assert any(c.nct_id == "NCT03785249" for c in rec.citations)


def test_agent_mcrc_msi_high_recommendation():
    """Verifies EvidenceAgent produces Level 1A Pembrolizumab for MSI-H colorectal cancer."""
    agent = EvidenceAgent()
    profile = PatientClinicalProfile(
        patient_id="PT-CRC-01",
        cancer_type="Colorectal Cancer",
        stage="Stage IV",
        somatic_mutations=["MSI-H", "dMMR"],
    )

    rec = agent.generate_recommendation(profile, enforce_safety_gate=False)
    assert "pembrolizumab" in rec.recommendation.lower()
    assert rec.evidence_level == EvidenceLevel.LEVEL_1A
    assert any(c.nct_id == "NCT02563002" for c in rec.citations)


def test_agent_prostate_crpc_recommendation():
    """Verifies EvidenceAgent produces Level 1A Olaparib for HRR-mutated mCRPC."""
    agent = EvidenceAgent()
    profile = PatientClinicalProfile(
        patient_id="PT-PR-01",
        cancer_type="Prostate Cancer",
        stage="Metastatic CRPC",
        somatic_mutations=["BRCA2 homozygous loss"],
    )

    rec = agent.generate_recommendation(profile, enforce_safety_gate=False)
    assert "olaparib" in rec.recommendation.lower()
    assert rec.evidence_level == EvidenceLevel.LEVEL_1A
    assert any(c.nct_id == "NCT04038502" for c in rec.citations)


def test_agent_breast_pik3ca_recommendation():
    """Verifies EvidenceAgent produces Level 1A Alpelisib + Fulvestrant for PIK3CA breast cancer."""
    agent = EvidenceAgent()
    profile = PatientClinicalProfile(
        patient_id="PT-BR-01",
        cancer_type="Breast Cancer",
        stage="Stage IV (HR+/HER2-)",
        somatic_mutations=["PIK3CA H1047R"],
    )

    rec = agent.generate_recommendation(profile, enforce_safety_gate=False)
    assert "alpelisib" in rec.recommendation.lower()
    assert rec.evidence_level == EvidenceLevel.LEVEL_1A
    assert any(c.nct_id == "NCT02437318" for c in rec.citations)
