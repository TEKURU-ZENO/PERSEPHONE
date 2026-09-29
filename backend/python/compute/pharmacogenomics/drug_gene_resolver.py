"""
Drug-gene resolution for the PERSEPHONE platform.
Provides static methods to lookup drug-gene interactions and contraindications.
"""

class DrugGeneResolver:
    """
    Resolves interactions between genes and therapeutic compounds.
    """
    
    _INTERACTION_DB = {
        "BRCA1": [{"drug": "Olaparib", "interaction_type": "synthetic_lethality", "evidence_level": "A", "source": "DrugBank:DB09071"}, {"drug": "Niraparib", "interaction_type": "synthetic_lethality", "evidence_level": "A", "source": "DrugBank:DB12332"}, {"drug": "Rucaparib", "interaction_type": "synthetic_lethality", "evidence_level": "A", "source": "DrugBank:DB12332"}],
        "EGFR": [{"drug": "Osimertinib", "interaction_type": "inhibitor", "evidence_level": "A", "source": "DrugBank:DB09330"}, {"drug": "Erlotinib", "interaction_type": "inhibitor", "evidence_level": "A", "source": "DrugBank:DB00530"}, {"drug": "Gefitinib", "interaction_type": "inhibitor", "evidence_level": "B", "source": "DrugBank:DB00317"}],
        "KRAS": [{"drug": "Adagrasib", "interaction_type": "inhibitor", "evidence_level": "A", "source": "DrugBank:DB17415"}, {"drug": "Sotorasib", "interaction_type": "inhibitor", "evidence_level": "A", "source": "DrugBank:DB16726"}],
        "BRAF": [{"drug": "Vemurafenib", "interaction_type": "inhibitor", "evidence_level": "A", "source": "DrugBank:DB08881"}, {"drug": "Dabrafenib", "interaction_type": "inhibitor", "evidence_level": "A", "source": "DrugBank:DB08912"}, {"drug": "Encorafenib", "interaction_type": "inhibitor", "evidence_level": "B", "source": "DrugBank:DB11718"}],
        "PIK3CA": [{"drug": "Alpelisib", "interaction_type": "inhibitor", "evidence_level": "A", "source": "DrugBank:DB12015"}],
        "ALK": [{"drug": "Crizotinib", "interaction_type": "inhibitor", "evidence_level": "A", "source": "DrugBank:DB08865"}, {"drug": "Alectinib", "interaction_type": "inhibitor", "evidence_level": "A", "source": "DrugBank:DB11363"}, {"drug": "Lorlatinib", "interaction_type": "inhibitor", "evidence_level": "A", "source": "DrugBank:DB14938"}],
        "TP53": [{"drug": "Pembrolizumab", "interaction_type": "immunotherapy_indicator", "evidence_level": "C", "source": "PharmGKB"}, {"drug": "Nivolumab", "interaction_type": "immunotherapy_indicator", "evidence_level": "C", "source": "PharmGKB"}]
    }

    _CONTRAINDICATION_MAP = {
        "EGFR": [{"drug": "Erlotinib", "reason": "T790M resistance mutation bypasses first-gen TKI binding"}],
        "KRAS": [{"drug": "Cetuximab", "reason": "KRAS mutations confer intrinsic resistance to anti-EGFR antibodies"}]
    }

    @staticmethod
    def resolve_interactions(gene, drug=None):
        """
        Returns list of interaction dicts for the gene; if drug is specified, filter to that drug; unknown genes return empty list
        """
        interactions = DrugGeneResolver._INTERACTION_DB.get(gene, [])
        if drug:
            interactions = [i for i in interactions if i["drug"] == drug]
        return interactions

    @staticmethod
    def get_contraindications(gene_variants):
        """
        Returns list of {gene, drug, reason} for drugs that are contraindicated.
        """
        results = []
        for gene in gene_variants:
            if gene in DrugGeneResolver._CONTRAINDICATION_MAP:
                for contra in DrugGeneResolver._CONTRAINDICATION_MAP[gene]:
                    results.append({
                        "gene": gene,
                        "drug": contra["drug"],
                        "reason": contra["reason"]
                    })
        return results
