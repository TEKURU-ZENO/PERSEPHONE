"""
Trial Evidence Linker module for PERSEPHONE Research Intelligence Platform.
Establishes bidirectional linking between Clinical Trials (NCT IDs), Literature Publications (PMIDs),
Evidence Items, and Clinical Practice Guidelines.
"""
from typing import Dict, List, Any, Optional
from backend.python.compute.research_intelligence.literature.retrieval import ONCOLOGY_LITERATURE_CORPUS
from backend.python.compute.research_intelligence.guidelines.sources import ALL_GUIDELINE_RULES

# Authoritative bidirectional registry linking NCT clinical trials to literature PMIDs and guidelines
TRIAL_EVIDENCE_MAP = {
    "NCT01844986": {
        "trial_id": "NCT01844986",
        "trial_name": "SOLO-1",
        "primary_pmid": "30345884",
        "secondary_pmids": ["33742491", "34902562"],
        "drug": "Olaparib",
        "condition": "Ovarian Cancer",
        "phase": "Phase III",
        "guideline_ids": ["NCCN-OV-001", "ASCO-OV-001", "ESMO-OV-001"],
        "evidence_summary": "Pivotal Phase III trial demonstrating 70% reduction in risk of progression/death for first-line maintenance Olaparib in BRCAm ovarian cancer."
    },
    "NCT02477644": {
        "trial_id": "NCT02477644",
        "trial_name": "PAOLA-1",
        "primary_pmid": "31851799",
        "secondary_pmids": ["36371801"],
        "drug": "Olaparib",
        "condition": "Ovarian Cancer",
        "phase": "Phase III",
        "guideline_ids": ["NCCN-OV-001", "ESMO-OV-001"],
        "evidence_summary": "Phase III trial demonstrating significant PFS improvement for Olaparib + Bevacizumab combination in HRD-positive advanced ovarian cancer."
    },
    "NCT02655016": {
        "trial_id": "NCT02655016",
        "trial_name": "PRIMA",
        "primary_pmid": "31562799",
        "secondary_pmids": [],
        "drug": "Niraparib",
        "condition": "Ovarian Cancer",
        "phase": "Phase III",
        "guideline_ids": ["NCCN-OV-002"],
        "evidence_summary": "Phase III trial showing first-line maintenance Niraparib significantly improves PFS across HRD+ and all-comer populations."
    },
    "NCT02296424": {
        "trial_id": "NCT02296424",
        "trial_name": "FLAURA",
        "primary_pmid": "29151359",
        "secondary_pmids": ["31751012"],
        "drug": "Osimertinib",
        "condition": "Non-Small Cell Lung Cancer",
        "phase": "Phase III",
        "guideline_ids": ["NCCN-NSCLC-001"],
        "evidence_summary": "Phase III trial establishing Osimertinib superiority in untreated EGFR-mutated advanced NSCLC."
    },
    "NCT03785249": {
        "trial_id": "NCT03785249",
        "trial_name": "KRYSTAL-1",
        "primary_pmid": "36546651",
        "secondary_pmids": [],
        "drug": "Adagrasib",
        "condition": "Colorectal Cancer",
        "phase": "Phase I/II",
        "guideline_ids": ["NCCN-CRC-001"],
        "evidence_summary": "Phase I/II study of Adagrasib ± Cetuximab in KRAS-mutated metastatic colorectal cancer."
    }
}


class TrialEvidenceLinker:
    """
    Resolves bidirectional relationships across trials, literature, and guidelines.
    """

    @classmethod
    def get_publications_for_trial(cls, nct_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves all primary and secondary published papers associated with a clinical trial.
        """
        clean_id = nct_id.strip().upper()
        mapping = TRIAL_EVIDENCE_MAP.get(clean_id)
        if not mapping:
            # Fallback scan across literature corpus
            return [p for p in ONCOLOGY_LITERATURE_CORPUS if p.get("nct_id", "").upper() == clean_id]

        target_pmids = set([mapping["primary_pmid"]] + mapping.get("secondary_pmids", []))
        return [p for p in ONCOLOGY_LITERATURE_CORPUS if p.get("pmid") in target_pmids]

    @classmethod
    def get_trial_for_publication(cls, pmid: str) -> Optional[Dict[str, Any]]:
        """
        Finds the trial associated with a publication PMID.
        """
        clean_pmid = str(pmid).strip()
        for trial_id, entry in TRIAL_EVIDENCE_MAP.items():
            if entry.get("primary_pmid") == clean_pmid or clean_pmid in entry.get("secondary_pmids", []):
                return entry
        return None

    @classmethod
    def build_trial_evidence_chain(cls, nct_id: str) -> Dict[str, Any]:
        """
        Builds the complete end-to-end evidence chain for a trial:
        Trial -> Publications -> Guidelines.
        """
        clean_id = nct_id.strip().upper()
        mapping = TRIAL_EVIDENCE_MAP.get(clean_id)
        if not mapping:
            return {"trial_id": clean_id, "status": "NO_EVIDENCE_MAPPED"}

        pubs = cls.get_publications_for_trial(clean_id)
        guidelines = [r.to_dict() for r in ALL_GUIDELINE_RULES if r.rule_id in mapping.get("guideline_ids", [])]

        return {
            "trial_id": clean_id,
            "trial_name": mapping.get("trial_name"),
            "drug": mapping.get("drug"),
            "condition": mapping.get("condition"),
            "phase": mapping.get("phase"),
            "evidence_summary": mapping.get("evidence_summary"),
            "primary_pmid": mapping.get("primary_pmid"),
            "publications": pubs,
            "guideline_recommendations": guidelines,
            "link_status": "VERIFIED"
        }
