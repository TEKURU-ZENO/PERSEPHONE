class PathwayEnrichmentEngine:
    """
    Computes pathway enrichment scores and hierarchy for a set of input genes.
    Useful for identifying key oncogenic signaling pathways disrupted in a tumor.
    """

    _PATHWAY_DB = [
        {"pathway_id": "R-HSA-5685939", "name": "Homologous Recombination", "genes": ["BRCA1", "BRCA2", "RAD51", "PALB2", "ATM", "CHEK2", "NBN"]},
        {"pathway_id": "R-HSA-177929", "name": "EGFR Kinase Signaling", "genes": ["EGFR", "GRB2", "SOS1", "GAB1", "ERBB2", "ERBB3"]},
        {"pathway_id": "R-HSA-5673001", "name": "RAS-MAPK Cascade", "genes": ["KRAS", "HRAS", "NRAS", "BRAF", "RAF1", "MAP2K1", "MAPK1"]},
        {"pathway_id": "R-HSA-2219528", "name": "PI3K-AKT Signaling", "genes": ["PIK3CA", "PIK3CB", "AKT1", "PTEN", "MTOR", "TSC1", "TSC2"]},
        {"pathway_id": "R-HSA-3700989", "name": "TP53 Regulation of Cell Death", "genes": ["TP53", "MDM2", "BAX", "BCL2", "CDKN1A", "CASP3"]},
        {"pathway_id": "R-HSA-9006931", "name": "ALK Signaling", "genes": ["ALK", "NPM1", "EML4", "STAT3", "JAK2"]},
        {"pathway_id": "R-HSA-1640170", "name": "DNA Mismatch Repair", "genes": ["MLH1", "MSH2", "MSH6", "PMS2", "EPCAM"]}
    ]

    @staticmethod
    def enrich_variants(variant_genes):
        """
        Calculates pathway enrichment for a list of variant genes.
        
        Args:
            variant_genes (list): List of gene strings.
            
        Returns:
            dict: Contains 'enriched_pathways' sorted by p_value ascending.
        """
        enriched_pathways = []
        variant_set = set(variant_genes)
        
        for pathway in PathwayEnrichmentEngine._PATHWAY_DB:
            pathway_genes = set(pathway["genes"])
            matched_genes = list(variant_set.intersection(pathway_genes))
            genes_hit = len(matched_genes)
            total_genes = len(pathway_genes)
            
            if genes_hit > 0:
                p_value = 0.001 * (total_genes / genes_hit)
                fold_enrichment = float(genes_hit) / total_genes * 10.0 # Mock factor
                
                enriched_pathways.append({
                    "pathway_id": pathway["pathway_id"],
                    "pathway_name": pathway["name"],
                    "p_value": p_value,
                    "genes_hit": genes_hit,
                    "total_genes": total_genes,
                    "fold_enrichment": fold_enrichment,
                    "matched_genes": matched_genes
                })
                
        enriched_pathways.sort(key=lambda x: x["p_value"])
        return {"enriched_pathways": enriched_pathways}

    @staticmethod
    def get_pathway_hierarchy(pathway_id):
        """
        Retrieves upstream and downstream connections for a pathway.
        
        Args:
            pathway_id (str): The Reactome pathway ID.
            
        Returns:
            dict: Pathway hierarchy including upstream and downstream lists.
        """
        return {
            "pathway_id": pathway_id,
            "name": next((p["name"] for p in PathwayEnrichmentEngine._PATHWAY_DB if p["pathway_id"] == pathway_id), "Unknown"),
            "upstream": ["R-HSA-0000001", "R-HSA-0000002"], # Mock data
            "downstream": ["R-HSA-0000003", "R-HSA-0000004"] # Mock data
        }

    @staticmethod
    def compute_pathway_impact_score(enriched_pathways):
        """
        Computes a normalized impact score for the affected pathways.
        
        Args:
            enriched_pathways (list): Output from enrich_variants.
            
        Returns:
            float: Score between 0.0 and 1.0.
        """
        if not enriched_pathways:
            return 0.0
            
        score_sum = sum((1.0 / p["p_value"]) * p["fold_enrichment"] for p in enriched_pathways if p["p_value"] > 0)
        normalization_factor = 10000.0 # Arbitrary large number for normalization
        
        impact_score = min(score_sum / normalization_factor, 1.0)
        return float(impact_score)
