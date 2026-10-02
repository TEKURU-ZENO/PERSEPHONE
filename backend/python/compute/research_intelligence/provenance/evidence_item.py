"""
Evidence Item module for PERSEPHONE Research Intelligence Platform.
Stores structured clinical observations while calculating cryptographic evidence hashes.
"""
import hashlib
from typing import Dict, Any, Optional


class EvidenceItem:
    """
    Represents an extracted, typed scientific evidence assertion derived from a ProvenanceSource.
    """
    def __init__(
        self,
        evidence_id: str,
        source_id: str,
        source_hash: str,
        study_design: str,
        sample_size: Optional[int],
        hazard_ratio: Optional[Dict[str, Any]],
        median_pfs_delta_months: Optional[float],
        cebm_level: str,
        grade_rating: str,
        nccn_category: Optional[str] = None,
        summary_statement: str = ""
    ):
        self.evidence_id = evidence_id
        self.source_id = source_id
        self.source_hash = source_hash
        self.study_design = study_design
        self.sample_size = sample_size
        self.hazard_ratio = hazard_ratio
        self.median_pfs_delta_months = median_pfs_delta_months
        self.cebm_level = cebm_level
        self.grade_rating = grade_rating
        self.nccn_category = nccn_category
        self.summary_statement = summary_statement

        # Compute immutable evidence extraction hash
        hash_payload = (
            f"{evidence_id}|{source_hash}|{study_design}|{sample_size}|"
            f"{hazard_ratio}|{median_pfs_delta_months}|{cebm_level}|{grade_rating}|{nccn_category}"
        )
        self.evidence_hash = hashlib.sha256(hash_payload.encode('utf-8')).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "source_id": self.source_id,
            "source_hash": self.source_hash,
            "study_design": self.study_design,
            "sample_size": self.sample_size,
            "hazard_ratio": self.hazard_ratio,
            "median_pfs_delta_months": self.median_pfs_delta_months,
            "quality": {
                "cebm_level": self.cebm_level,
                "grade_rating": self.grade_rating,
                "nccn_category": self.nccn_category
            },
            "summary_statement": self.summary_statement,
            "evidence_hash": self.evidence_hash
        }
