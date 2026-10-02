"""
Evidence Snapshot module for PERSEPHONE Research Intelligence Platform.
Captures immutable versioned snapshots for exact deterministic reproducibility of research graphs.
"""
import hashlib
import time
from typing import Dict, Any, Optional


class EvidenceSnapshot:
    """
    Immutable versioned snapshot of evidence and literature content.
    """
    def __init__(
        self,
        snapshot_id: str,
        source_id: str,
        content_hash: str,
        parser_version: str = "guideline-parser-v1",
        extractor_version: str = "evidence-extractor-v1",
        model_version: str = "research-intel-v1",
        retrieval_timestamp: Optional[str] = None
    ):
        self.snapshot_id = snapshot_id
        self.source_id = source_id
        self.content_hash = content_hash
        self.parser_version = parser_version
        self.extractor_version = extractor_version
        self.model_version = model_version
        self.retrieval_timestamp = retrieval_timestamp or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # Snapshot cryptographic digest
        digest_input = f"{snapshot_id}|{source_id}|{content_hash}|{parser_version}|{extractor_version}|{model_version}"
        self.snapshot_digest = hashlib.sha256(digest_input.encode('utf-8')).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "source_id": self.source_id,
            "content_hash": self.content_hash,
            "parser_version": self.parser_version,
            "extractor_version": self.extractor_version,
            "model_version": self.model_version,
            "retrieval_timestamp": self.retrieval_timestamp,
            "snapshot_digest": self.snapshot_digest
        }
