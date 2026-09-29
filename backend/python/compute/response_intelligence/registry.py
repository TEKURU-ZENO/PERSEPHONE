"""
Response Intelligence Registry module for PERSEPHONE.
Provides unified dispatch and telemetry profiling for multimodal digital biomarker,
treatment response prediction, and resistance escape pipelines.
"""
import time
from backend.python.compute.response_intelligence.fusion import MultimodalResponseFusion
from backend.python.compute.response_intelligence.biomarkers.digital import DigitalBiomarkerEngine
from backend.python.compute.response_intelligence.biomarkers.imaging import ImagingBiomarkerExtractor
from backend.python.compute.response_intelligence.biomarkers.genomic import GenomicBiomarkerExtractor
from backend.python.compute.response_intelligence.biomarkers.composite import CompositeBiomarkerSynthesizer
from backend.python.compute.response_intelligence.response.classifier import MultimodalResponseClassifier
from backend.python.compute.response_intelligence.response.predictor import TreatmentResponsePredictor
from backend.python.compute.response_intelligence.response.kinetics import ResponseKineticsModeler
from backend.python.compute.response_intelligence.resistance.detector import ResistanceMechanismDetector
from backend.python.compute.response_intelligence.resistance.predictor import ResistanceEscapePredictor

class ResponseIntelligenceRegistry:
    """
    Public registry interface for Response Intelligence compute routines.
    """

    @classmethod
    def extract_biomarkers(cls, patient_data=None):
        start = time.perf_counter()
        vector = MultimodalResponseFusion.fuse(patient_data)
        digital = DigitalBiomarkerEngine.compute_digital_biomarker(vector)
        imaging = ImagingBiomarkerExtractor.extract_imaging_biomarkers(vector)
        genomic = GenomicBiomarkerExtractor.extract_genomic_biomarkers(vector)
        composite = CompositeBiomarkerSynthesizer.synthesize_composite(vector)
        elapsed = round((time.perf_counter() - start) * 1000, 2)

        return {
            "digital": digital,
            "imaging": imaging,
            "genomic": genomic,
            "composite": composite,
            "provenance": vector.provenance,
            "processingTimeMs": elapsed
        }

    @classmethod
    def predict_response(cls, patient_data=None, proposed_drug="Olaparib"):
        start = time.perf_counter()
        vector = MultimodalResponseFusion.fuse(patient_data)
        prediction = TreatmentResponsePredictor.predict_response(vector, proposed_drug=proposed_drug)
        classification = MultimodalResponseClassifier.classify_response(vector)
        kinetics = ResponseKineticsModeler.model_kinetics(vector)
        elapsed = round((time.perf_counter() - start) * 1000, 2)

        return {
            "prediction": prediction,
            "classification": classification,
            "kinetics": kinetics,
            "provenance": vector.provenance,
            "processingTimeMs": elapsed
        }

    @classmethod
    def analyze_resistance(cls, patient_data=None):
        start = time.perf_counter()
        vector = MultimodalResponseFusion.fuse(patient_data)
        detector = ResistanceMechanismDetector.detect_mechanisms(vector)
        escape = ResistanceEscapePredictor.predict_escape(vector)
        elapsed = round((time.perf_counter() - start) * 1000, 2)

        return {
            "detection": detector,
            "escape_prediction": escape,
            "provenance": vector.provenance,
            "processingTimeMs": elapsed
        }

    @classmethod
    def run_full_response_intelligence(cls, patient_data=None):
        start = time.perf_counter()
        vector = MultimodalResponseFusion.fuse(patient_data)
        drug = (patient_data or {}).get("proposed_drug", "Olaparib")

        biomarkers = {
            "digital": DigitalBiomarkerEngine.compute_digital_biomarker(vector),
            "imaging": ImagingBiomarkerExtractor.extract_imaging_biomarkers(vector),
            "genomic": GenomicBiomarkerExtractor.extract_genomic_biomarkers(vector),
            "composite": CompositeBiomarkerSynthesizer.synthesize_composite(vector)
        }
        response = {
            "prediction": TreatmentResponsePredictor.predict_response(vector, proposed_drug=drug),
            "classification": MultimodalResponseClassifier.classify_response(vector),
            "kinetics": ResponseKineticsModeler.model_kinetics(vector)
        }
        resistance = {
            "detection": ResistanceMechanismDetector.detect_mechanisms(vector),
            "escape_prediction": ResistanceEscapePredictor.predict_escape(vector)
        }

        elapsed = round((time.perf_counter() - start) * 1000, 2)

        return {
            "multimodal_vector": vector.to_dict(),
            "biomarkers": biomarkers,
            "response": response,
            "resistance": resistance,
            "processingTimeMs": elapsed
        }
