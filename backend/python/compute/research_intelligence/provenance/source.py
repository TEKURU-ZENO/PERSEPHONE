"""
Provenance Source module for PERSEPHONE Research Intelligence Platform.
Defines typed source registries and cryptographic content hashing for research entities.
"""
import hashlib
import time
from typing import Dict, Any, Optional


class ProvenanceSource:
    """
    Represents an immutable, typed research provenance source.
    """
    VALID_SOURCE_TYPES = {"PUBMED", "CLINICAL_TRIAL", "GUIDELINE", "AGENT", "COMPUTED_MODEL"}

    def __init__(
        self,
        source_id: str,
        source_type: str,
        uri: str,
        version: str,
        title: str,
        raw_content: Optional[str] = None,
        retrieved_at: Optional[str] = None
    ):
        if source_type not in self.VALID_SOURCE_TYPES:
            raise ValueError(f"Invalid source_type: {source_type}. Must be one of {self.VALID_SOURCE_TYPES}")
        self.source_id = source_id
        self.source_type = source_type
        self.uri = uri
        self.version = version
        self.title = title
        self.retrieved_at = retrieved_at or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        
        # Calculate immutable source content hash
        content_payload = f"{source_id}|{source_type}|{uri}|{version}|{raw_content or ''}"
        self.content_hash = hashlib.sha256(content_payload.encode('utf-8')).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "source_type": self.source_type,
            "uri": self.uri,
            "version": self.version,
            "title": self.title,
            "retrieved_at": self.retrieved_at,
            "content_hash": self.content_hash
        }
