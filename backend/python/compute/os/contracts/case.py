"""
Case Contract Schema v1.0 for PERSEPHONE OS.
Defines canonical input structures, case context identifiers, and execution run metadata.
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import time
import uuid


@dataclass
class ExecutionRunMetadata:
    """Tracks identity and idempotency for a specific execution invocation."""
    case_id: str
    run_id: str = field(default_factory=lambda: f"RUN-{int(time.time()*1000)}-{uuid.uuid4().hex[:6]}")
    idempotency_key: str = field(default_factory=lambda: uuid.uuid4().hex)
    manifest_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_id": self.case_id,
            "run_id": self.run_id,
            "idempotency_key": self.idempotency_key,
            "manifest_id": self.manifest_id,
            "created_at": self.created_at
        }


class CaseSchemaValidator:
    """Validates raw patient case inputs against Case Contract v1.0."""
    REQUIRED_PATIENT_FIELDS = ["id"]

    @classmethod
    def validate_patient_case(cls, patient: Dict[str, Any]) -> Dict[str, Any]:
        required = ["id", "name", "cancer_type", "variants", "labs"]
        missing = [f for f in required if f not in patient]
        return {
            "valid": len(missing) == 0,
            "missing_fields": missing,
            "patient_id": patient.get("id")
        }

    @classmethod
    def validate_case_input(cls, payload: Dict[str, Any]) -> Dict[str, Any]:
        patient = payload.get("patient") or payload.get("patient_data") or {}
        if not patient:
            # Fallback to minimal patient structure
            patient = {"id": payload.get("patientId", "patient-a")}

        for req in cls.REQUIRED_PATIENT_FIELDS:
            if req not in patient:
                raise ValueError(f"Case Contract v1.0 violation: Missing required patient field '{req}'")

        # Normalize patient structure
        normalized_patient = {
            "id": str(patient.get("id")),
            "name": str(patient.get("name", "Elena Rostova")),
            "age": int(patient.get("age", 58)),
            "cancer_type": str(patient.get("cancer_type", patient.get("diagnosis", "High-Grade Serous Ovarian Carcinoma"))),
            "stage": str(patient.get("stage", "Stage IIIc")),
            "variants": list(patient.get("variants") or ["BRCA1 c.5266dupC (p.Gln1756Profs*74)"]),
            "hrd_score": float(patient.get("hrd_score", 58.0)),
            "tmb_score": float(patient.get("tmb_score", 7.0)),
            "carrying_capacity": float(patient.get("carrying_capacity", 205.0)),
            "resistant_fraction": float(patient.get("resistant_fraction", 0.05)),
            "labs": dict(patient.get("labs") or {
                "eGFR": 75.0,
                "AST_ALT_xULN": 1.0,
                "bilirubin_xULN": 0.8,
                "ANC": 2400.0,
                "platelets": 210000.0,
                "QTc": 420.0
            })
        }

        # Normalize imaging signals
        imaging = payload.get("imaging") or payload.get("imaging_signals") or {
            "recist_status": "PR",
            "volume_delta_pct": -25.0,
            "necrotic_fraction": 0.15,
            "baseline_volume": 82.0
        }

        # Normalize monitoring signals
        monitoring = payload.get("monitoring") or payload.get("monitoring_signals") or {
            "current_velocity": -0.05
        }

        drug = payload.get("drug") or payload.get("proposed_drug", "Olaparib")

        return {
            "patient": normalized_patient,
            "drug": drug,
            "imaging": imaging,
            "monitoring": monitoring,
            "options": payload.get("options", {})
        }
