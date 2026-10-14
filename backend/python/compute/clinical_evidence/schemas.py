"""
backend/python/compute/clinical_evidence/schemas.py

Pydantic schemas for the Clinical Evidence Agent, Safety Gate,
and AI Evaluation Benchmark suite (Tasks C1, C2, C3).
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EvidenceLevel(str, Enum):
    LEVEL_1A = "1A"  # High-powered meta-analysis or multi-center randomized controlled Phase 3 trials
    LEVEL_1B = "1B"  # Single randomized controlled trial with narrow CI
    LEVEL_2A = "2A"  # Prospective well-designed non-randomized cohort / registry study
    LEVEL_2B = "2B"  # Retrospective cohort or case-control study
    LEVEL_3 = "3"    # Case series or non-consecutive study
    LEVEL_4 = "4"    # Preclinical / bench evidence or expert opinion consensus
    NOT_APPLICABLE = "N/A"


class Citation(BaseModel):
    nct_id: Optional[str] = Field(default=None, description="ClinicalTrials.gov identifier (e.g., NCT01844986)")
    title: str = Field(description="Title of published clinical trial, protocol, or manuscript")
    pmid: Optional[str] = Field(default=None, description="PubMed Identifier")


class PatientClinicalProfile(BaseModel):
    patient_id: str = Field(description="Unique patient identifier")
    cancer_type: str = Field(description="Primary cancer type (e.g., High-Grade Serous Ovarian Cancer, NSCLC, Colorectal Cancer)")
    stage: str = Field(description="Clinical or pathological staging (e.g., Stage IIIC, Stage IVB)")
    histology: Optional[str] = Field(default=None, description="Histopathological subtype")
    somatic_mutations: List[str] = Field(default_factory=list, description="List of detected somatic gene variants (e.g. ['BRCA1 c.5266dupC', 'TP53 R175H'])")
    germline_variants: List[str] = Field(default_factory=list, description="List of inherited germline pathogenic mutations")
    prior_therapies: List[str] = Field(default_factory=list, description="Previous systemic therapies and regimens (e.g. ['Carboplatin + Paclitaxel'])")
    allergies_hypersensitivities: List[str] = Field(default_factory=list, description="Known drug allergies and hypersensitivity history")
    organ_function: Dict[str, Any] = Field(default_factory=dict, description="Organ status lab values (creatinine, ANC, AST/ALT, bilirubin)")


class EvidenceRecommendation(BaseModel):
    recommendation: Optional[str] = Field(default=None, description="Specific drug or combination regimen recommendation")
    rationale: str = Field(default="", description="Mechanistic and biomarker-driven clinical reasoning")
    evidence_level: EvidenceLevel = Field(default=EvidenceLevel.NOT_APPLICABLE, description="NCCN/ASCO evidence tier (1A, 1B, 2A, 2B, 3, 4)")
    citations: List[Citation] = Field(default_factory=list, description="Curated literature citations supporting the regimen")
    cited_trial_ids: List[str] = Field(default_factory=list, description="ClinicalTrials.gov identifier list")
    cited_pmids: List[str] = Field(default_factory=list, description="PubMed PMID list")
    contraindications: List[str] = Field(default_factory=list, description="Identified relative or absolute contraindications")
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Calibrated clinical confidence score")
    abstain: bool = Field(default=False, description="Flag indicating model abstains from recommendation")
    abstain_reason: Optional[str] = Field(default=None, description="Reason code if abstained (e.g. NO_EVIDENCE, REJECTED_TARGET_MISMATCH)")
    source: str = Field(default="deterministic_fallback", description="'llm_evidence_agent' or 'deterministic_fallback'")
    safety_gate_passed: bool = Field(default=True, description="Whether all deterministic safety rules passed")
    safety_violations: List[str] = Field(default_factory=list, description="Explanations of any blocked safety violations")
    requires_oncologist_override: bool = Field(default=False, description="Flag indicating mandatory human sign-off needed")
    override_reason: Optional[str] = Field(default=None, description="Clinical justification for override requirement")


class SafetyCheckResult(BaseModel):
    passed: bool
    violations: List[str] = Field(default_factory=list)
    reason_code: Optional[str] = None
    requires_override: bool = False
    override_reason: Optional[str] = None
    substitute_recommendation: Optional[str] = None


class ClinicalEvaluationCase(BaseModel):
    case_id: str
    cancer_type: str
    stage: str
    somatic_mutations: List[str]
    germline_variants: List[str] = Field(default_factory=list)
    prior_therapies: List[str] = Field(default_factory=list)
    allergies_hypersensitivities: List[str] = Field(default_factory=list)
    proposed_drug_or_query: str
    ground_truth_acceptable_regimens: List[str]
    ground_truth_contraindicated_regimens: List[str]
    expected_evidence_level: str
    is_safety_trap: bool = False
    trap_rationale: Optional[str] = None
    expected_abstain: bool = False
    expected_abstain_reason: Optional[str] = None
    patient_name: Optional[str] = None
