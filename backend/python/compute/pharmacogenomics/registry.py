"""
Pharmacogenomics registry module.
"""
import time
from backend.python.compute.pharmacogenomics.drug_gene_resolver import DrugGeneResolver
from backend.python.compute.pharmacogenomics.sensitivity_predictor import SensitivityPredictor
from backend.python.compute.pharmacogenomics.resistance_mapper import ResistanceMapper
from backend.python.compute.pharmacogenomics.synergy_estimator import SynergyEstimator

class PharmacogenomicsRegistry:
    """Orchestrates pharmacogenomics pipelines."""

    @staticmethod
    def run_pharmacogenomics_pipeline(gene_variants, drug_candidates=None):
        """Runs the comprehensive pharmacogenomics analysis pipeline."""
        start_time = time.time()
        
        # Discover drugs if none provided
        if drug_candidates is None:
            drug_candidates = set()
            for gene in gene_variants:
                interactions = DrugGeneResolver.resolve_interactions(gene)
                for interaction in interactions:
                    drug_candidates.add(interaction["drug"])
            drug_candidates = list(drug_candidates)
            
        interactions_list = []
        for gene in gene_variants:
            interactions_list.extend(DrugGeneResolver.resolve_interactions(gene))
            
        contraindications = DrugGeneResolver.get_contraindications(gene_variants)
        
        predictions = SensitivityPredictor.predict_sensitivity(gene_variants, drug_candidates)
        ranked_drugs = SensitivityPredictor.rank_drugs(predictions)
        
        resistance = ResistanceMapper.map_resistance_mechanisms(gene_variants)
        
        # estimate synergy for top drugs
        top_drugs = list(dict.fromkeys([d["drug"] for d in ranked_drugs[:5]]))
        synergy_matrix = SynergyEstimator.rank_combinations(top_drugs, gene_variants)
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        return {
            "interactions": interactions_list,
            "sensitivity_predictions": predictions,
            "ranked_drugs": ranked_drugs,
            "resistance_mechanisms": resistance,
            "contraindications": contraindications,
            "synergy_matrix": synergy_matrix,
            "processing_time_ms": processing_time_ms
        }
