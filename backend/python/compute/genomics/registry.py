import time
from backend.python.compute.genomics.variant_annotator import VariantAnnotator
from backend.python.compute.genomics.pathway_enrichment import PathwayEnrichmentEngine
from backend.python.compute.genomics.biomarker_scorer import BiomarkerScorer
from backend.python.compute.genomics.signature_classifier import MutationSignatureClassifier

class GenomicsRegistry:
    """
    Orchestrates the entire genomic intelligence pipeline for PERSEPHONE.
    Processes patient variant profiles through annotation, pathway enrichment,
    biomarker scoring, and signature classification.
    """

    @staticmethod
    def run_genomic_pipeline(patient_variants):
        """
        Executes the genomic pipeline.
        
        Args:
            patient_variants (dict): Contains 'genes', 'variant_count', 'microsatellite_loci'.
            
        Returns:
            dict: Comprehensive genomic report.
        """
        start_time = time.time()
        
        genes = patient_variants.get("genes", [])
        variant_count = patient_variants.get("variant_count", 0)
        msi_loci = patient_variants.get("microsatellite_loci", [])
        
        # 1. Annotate
        annotated_variants = VariantAnnotator.annotate_panel(genes)
        
        # 2. Enrich pathways
        pathway_enrichment = PathwayEnrichmentEngine.enrich_variants(genes)
        pathway_impact = PathwayEnrichmentEngine.compute_pathway_impact_score(pathway_enrichment.get("enriched_pathways", []))
        
        # 3. Score & Rank Biomarkers
        ranked_biomarkers = BiomarkerScorer.rank_biomarkers(annotated_variants)
        
        # 4. Classify Signatures, TMB, MSI
        mutation_signature = MutationSignatureClassifier.classify_signature({"genes": genes})
        tmb = MutationSignatureClassifier.compute_tmb(variant_count)
        msi = MutationSignatureClassifier.compute_msi_score(msi_loci)
        
        end_time = time.time()
        processing_time_ms = int((end_time - start_time) * 1000)
        
        return {
            "annotated_variants": annotated_variants,
            "pathway_enrichment": pathway_enrichment,
            "ranked_biomarkers": ranked_biomarkers,
            "mutation_signature": mutation_signature,
            "tmb": tmb,
            "msi": msi,
            "pathway_impact_score": pathway_impact,
            "processing_time_ms": processing_time_ms
        }
