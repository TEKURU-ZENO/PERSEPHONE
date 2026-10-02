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
        
        canonical_hgvsc = {
            "BRCA1": "c.1961delA",
            "EGFR": "c.2573T>G",
            "KRAS": "c.35G>A",
            "TP53": "c.524G>A",
            "BRAF": "c.1799T>A",
            "PIK3CA": "c.3140A>G",
            "ALK": "fusion"
        }
        raw_variants = patient_variants.get("variants")
        if not raw_variants:
            raw_variants = []
            for g in genes:
                if isinstance(g, dict):
                    raw_variants.append(g)
                elif isinstance(g, (list, tuple)) and len(g) == 2:
                    raw_variants.append({"gene": g[0], "hgvsc": g[1]})
                else:
                    raw_variants.append({"gene": str(g), "hgvsc": canonical_hgvsc.get(str(g), "c.unknown")})

        # 1. Annotate
        annotated_variants = VariantAnnotator.annotate_panel(raw_variants)
        
        # 2. Enrich pathways
        pathway_enrichment = PathwayEnrichmentEngine.enrich_variants(genes)
        pathway_impact = PathwayEnrichmentEngine.compute_pathway_impact_score(pathway_enrichment.get("enriched_pathways", []))
        
        # 3. Score & Rank Biomarkers
        ranked_biomarkers = BiomarkerScorer.rank_biomarkers(annotated_variants)
        
        # 4. Classify Signatures, TMB, MSI
        counts_96 = patient_variants.get("counts_96") or patient_variants.get("trinucleotide_counts")
        if counts_96 is None:
            counts_96 = MutationSignatureClassifier.generate_synthetic_counts(genes, total_mutations=max(50, variant_count * 5 if variant_count else 100))
        mutation_signature = MutationSignatureClassifier.classify_signature(counts_96)
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
