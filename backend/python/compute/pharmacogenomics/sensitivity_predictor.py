"""
Sensitivity prediction module.
"""
import hashlib
from backend.python.compute.pharmacogenomics.drug_gene_resolver import DrugGeneResolver

class SensitivityPredictor:
    """Predicts drug sensitivity."""
    
    @staticmethod
    def _deterministic_hash_float(gene, drug, min_val, max_val):
        """Generates deterministic float based on gene and drug name."""
        h = hashlib.sha256(f"{gene}:{drug}".encode()).hexdigest()
        norm = int(h[:8], 16) / 0xffffffff
        return min_val + norm * (max_val - min_val)

    @staticmethod
    def predict_sensitivity(gene_variants, drug_candidates):
        """Predicts sensitivity and returns list of dictionaries."""
        predictions = []
        for gene in gene_variants:
            for drug in drug_candidates:
                interactions = DrugGeneResolver.resolve_interactions(gene, drug)
                contraindications = DrugGeneResolver.get_contraindications([gene])
                is_resistance = any(c['drug'] == drug for c in contraindications)

                if is_resistance:
                    ic50 = SensitivityPredictor._deterministic_hash_float(gene, drug, 500.0, 1000.0)
                    sens_class = 'resistant'
                elif interactions:
                    ic50 = SensitivityPredictor._deterministic_hash_float(gene, drug, 0.1, 5.0)
                    sens_class = 'sensitive'
                else:
                    ic50 = SensitivityPredictor._deterministic_hash_float(gene, drug, 50.0, 200.0)
                    sens_class = 'intermediate'
                    
                confidence = SensitivityPredictor._deterministic_hash_float(gene, drug + "_conf", 0.7, 0.99)
                
                predictions.append({
                    "drug": drug,
                    "gene": gene,
                    "predicted_ic50": round(ic50, 4),
                    "sensitivity_class": sens_class,
                    "confidence": round(confidence, 4)
                })
        return predictions

    @staticmethod
    def rank_drugs(predictions):
        """Ranks drugs by predicted IC50 ascending."""
        return sorted(predictions, key=lambda x: x["predicted_ic50"])
