"""
Resistance mapper module.
"""

class ResistanceMapper:
    """Maps and predicts drug resistance mechanisms."""
    
    _RESISTANCE_DB = {
        "EGFR": [{"variant": "T790M", "mechanism": "Gatekeeper mutation sterically blocks first-gen TKI binding", "resistance_type": "acquired", "bypass_pathway": "MET amplification", "alternative_drugs": ["Osimertinib"]}, {"variant": "C797S", "mechanism": "Covalent binding site mutation blocks third-gen TKI", "resistance_type": "acquired", "bypass_pathway": "EGFR amplification", "alternative_drugs": ["Combination therapy"]}],
        "BRAF": [{"variant": "V600E splice variant", "mechanism": "BRAF splice variants restore MAPK signaling", "resistance_type": "acquired", "bypass_pathway": "MEK reactivation", "alternative_drugs": ["Trametinib"]}],
        "KRAS": [{"variant": "G12D", "mechanism": "Adaptive feedback reactivation of RTK signaling", "resistance_type": "intrinsic", "bypass_pathway": "PI3K-AKT bypass", "alternative_drugs": ["Combination with SHP2 inhibitor"]}],
        "ALK": [{"variant": "G1202R", "mechanism": "Solvent-front mutation reduces ALK inhibitor binding", "resistance_type": "acquired", "bypass_pathway": "None", "alternative_drugs": ["Lorlatinib"]}]
    }

    @staticmethod
    def map_resistance_mechanisms(gene_variants, current_therapy=None):
        """Returns resistance mechanisms mapped to the provided genes."""
        results = []
        for gene in gene_variants:
            mechanisms = ResistanceMapper._RESISTANCE_DB.get(gene, [])
            for m in mechanisms:
                result = m.copy()
                result["gene"] = gene
                results.append(result)
        return results

    @staticmethod
    def predict_resistance_timeline(mechanism, tumor_evolution_data=None):
        """Predicts timeline to resistance based on mechanism."""
        res_type = mechanism.get("resistance_type", "acquired")
        if res_type == "intrinsic":
            months = 0
            factors = ["Intrinsic resistance detected"]
            confidence = 0.95
        else:
            months = 12
            factors = ["Average acquired resistance timeline based on variant"]
            confidence = 0.80
            
        return {
            "estimated_months_to_resistance": months,
            "confidence": confidence,
            "factors": factors
        }
