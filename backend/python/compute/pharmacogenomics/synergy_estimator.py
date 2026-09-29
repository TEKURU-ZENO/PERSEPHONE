"""
Synergy estimator module.
"""

class SynergyEstimator:
    """Estimates synergy between drugs."""
    
    _SYNERGY_DB = {
        ("Olaparib", "Pembrolizumab"): {"score": 0.72, "type": "synergistic", "mechanism": "PARP inhibition + PD-1 blockade enhances neoantigen presentation"},
        ("Dabrafenib", "Trametinib"): {"score": 0.85, "type": "synergistic", "mechanism": "BRAF + MEK dual inhibition prevents MAPK reactivation"},
        ("Osimertinib", "Bevacizumab"): {"score": 0.45, "type": "synergistic", "mechanism": "EGFR TKI + anti-VEGF dual pathway suppression"},
        ("Adagrasib", "Cetuximab"): {"score": 0.60, "type": "synergistic", "mechanism": "KRAS inhibition + EGFR blockade prevents feedback reactivation"}
    }

    @staticmethod
    def estimate_synergy(drug_a, drug_b, gene_context=None):
        """Estimates synergy score and type for drug combination."""
        pair1 = (drug_a, drug_b)
        pair2 = (drug_b, drug_a)
        
        if pair1 in SynergyEstimator._SYNERGY_DB:
            record = SynergyEstimator._SYNERGY_DB[pair1]
            return {
                "synergy_score": record["score"],
                "interaction_type": record["type"],
                "mechanism": record["mechanism"],
                "confidence": 0.85
            }
        elif pair2 in SynergyEstimator._SYNERGY_DB:
            record = SynergyEstimator._SYNERGY_DB[pair2]
            return {
                "synergy_score": record["score"],
                "interaction_type": record["type"],
                "mechanism": record["mechanism"],
                "confidence": 0.85
            }
        else:
            return {
                "synergy_score": 0.0,
                "interaction_type": "additive",
                "mechanism": "Unknown interaction, presumed additive",
                "confidence": 0.50
            }

    @staticmethod
    def rank_combinations(drug_list, gene_context=None):
        """Ranks all pairwise drug combinations by synergy score."""
        results = []
        n = len(drug_list)
        for i in range(n):
            for j in range(i + 1, n):
                syn = SynergyEstimator.estimate_synergy(drug_list[i], drug_list[j], gene_context)
                results.append({
                    "drug_a": drug_list[i],
                    "drug_b": drug_list[j],
                    "synergy": syn
                })
        return sorted(results, key=lambda x: x["synergy"]["synergy_score"], reverse=True)
