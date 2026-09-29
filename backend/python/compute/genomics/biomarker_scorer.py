class BiomarkerScorer:
    """
    Scores and ranks genomic biomarkers to assess clinical actionability
    and therapeutic implications for precision oncology.
    """

    @staticmethod
    def score_actionability(annotated_variant):
        """
        Determines the actionability tier for a given annotated variant.
        
        Args:
            annotated_variant (dict): Annotated variant dictionary.
            
        Returns:
            dict: Contains actionability_tier, evidence_level, and therapeutic_implications.
        """
        gene = annotated_variant.get("gene", "")
        clinical_sig = annotated_variant.get("clinical_significance", "VUS")
        evidence_level = annotated_variant.get("evidence_level", "D")
        
        tier = "Tier III"
        if clinical_sig == "Pathogenic":
            if evidence_level == "A":
                tier = "Tier I-A"
            elif evidence_level == "B":
                tier = "Tier I-B"
            elif evidence_level == "C":
                tier = "Tier II-C"
            elif evidence_level == "D":
                tier = "Tier II-D"
        elif clinical_sig == "Benign" or clinical_sig == "Likely Benign":
            tier = "Tier IV"
            
        therapies = {
            "BRCA1": "PARP inhibitor candidate",
            "EGFR": "TKI candidate (erlotinib/osimertinib)",
            "KRAS": "KRAS G12D inhibitor candidate (adagrasib)",
            "TP53": "Monitor; consider immunotherapy if TMB-H",
            "BRAF": "BRAF inhibitor candidate (vemurafenib/dabrafenib)",
            "PIK3CA": "PI3K inhibitor candidate (alpelisib)",
            "ALK": "ALK inhibitor candidate (crizotinib/alectinib)"
        }
        
        therapeutic_implications = therapies.get(gene, "No specific targeted therapy indicated")
        
        return {
            "actionability_tier": tier,
            "evidence_level": evidence_level,
            "therapeutic_implications": therapeutic_implications
        }

    @staticmethod
    def rank_biomarkers(annotated_variants):
        """
        Ranks a list of annotated variants based on actionability tiers.
        
        Args:
            annotated_variants (list): List of annotated variant dictionaries.
            
        Returns:
            list: Sorted list of variants with 'rank' and 'actionability' added.
        """
        tier_values = {
            "Tier I-A": 1,
            "Tier I-B": 2,
            "Tier II-C": 3,
            "Tier II-D": 4,
            "Tier III": 5,
            "Tier IV": 6
        }
        
        scored = []
        for variant in annotated_variants:
            actionability = BiomarkerScorer.score_actionability(variant)
            scored.append({
                **variant,
                **actionability
            })
            
        scored.sort(key=lambda x: tier_values.get(x["actionability_tier"], 99))
        
        for idx, variant in enumerate(scored):
            variant["rank"] = idx + 1
            
        return scored

    @staticmethod
    def classify_evidence_tier(variant, indication=None):
        """
        Classifies the evidence tier directly from a variant.
        
        Args:
            variant (dict): Variant dictionary.
            indication (str, optional): Clinical indication.
            
        Returns:
            str: Evidence tier 'A', 'B', 'C', or 'D'.
        """
        sig = variant.get("clinical_significance", "VUS")
        freq = variant.get("somatic_frequency", 0.0)
        
        if sig == "Pathogenic" and freq > 0.1:
            return "A"
        elif sig == "Pathogenic":
            return "B"
        elif sig == "Likely Pathogenic":
            return "C"
        else:
            return "D"
