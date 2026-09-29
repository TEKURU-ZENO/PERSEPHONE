class VariantAnnotator:
    """
    Annotates genomic variants with clinical and somatic significance.
    Combines data from ClinVar and COSMIC databases to provide a comprehensive
    view of variant pathogenicity and prevalence in cancer.
    """

    _CLINVAR_DB = {
        "BRCA1": {"variation_id": "VCV000055474", "variant_name": "BRCA1 c.1961delA", "hgvsc": "c.1961delA", "classification": "Pathogenic", "consequence": "Frameshift leading to Homologous Recombination Deficiency (HRD)", "disease": "Hereditary breast and ovarian cancer", "allele_frequency": 0.0003},
        "EGFR": {"variation_id": "VCV000016618", "variant_name": "EGFR L858R", "hgvsc": "c.2573T>G", "classification": "Pathogenic", "consequence": "Constitutive kinase domain activation", "disease": "Non-small cell lung cancer", "allele_frequency": 0.0012},
        "KRAS": {"variation_id": "VCV000012574", "variant_name": "KRAS G12D", "hgvsc": "c.35G>A", "classification": "Pathogenic", "consequence": "Hotspot mutation trapping GTP-bound active state", "disease": "Pancreatic adenocarcinoma", "allele_frequency": 0.0045},
        "TP53": {"variation_id": "VCV000012356", "variant_name": "TP53 R175H", "hgvsc": "c.524G>A", "classification": "Pathogenic", "consequence": "Loss of tumor suppressor function", "disease": "Li-Fraumeni syndrome", "allele_frequency": 0.0008},
        "BRAF": {"variation_id": "VCV000013959", "variant_name": "BRAF V600E", "hgvsc": "c.1799T>A", "classification": "Pathogenic", "consequence": "Constitutive MAPK pathway activation", "disease": "Melanoma", "allele_frequency": 0.0021},
        "PIK3CA": {"variation_id": "VCV000017690", "variant_name": "PIK3CA H1047R", "hgvsc": "c.3140A>G", "classification": "Pathogenic", "consequence": "PI3K-AKT pathway hyperactivation", "disease": "Breast cancer", "allele_frequency": 0.0018},
        "ALK": {"variation_id": "VCV000030711", "variant_name": "EML4-ALK fusion", "hgvsc": "fusion", "classification": "Pathogenic", "consequence": "Constitutive ALK kinase activation via fusion", "disease": "Non-small cell lung cancer", "allele_frequency": 0.0005}
    }

    _COSMIC_DB = {
        "BRCA1": {"cosmic_id": "COSM20001", "mutation_type": "frameshift", "tissue": "ovary", "somatic_frequency": 0.04},
        "EGFR": {"cosmic_id": "COSM6224", "mutation_type": "missense", "tissue": "lung", "somatic_frequency": 0.15},
        "KRAS": {"cosmic_id": "COSM521", "mutation_type": "missense", "tissue": "pancreas", "somatic_frequency": 0.30},
        "TP53": {"cosmic_id": "COSM10648", "mutation_type": "missense", "tissue": "multiple", "somatic_frequency": 0.28},
        "BRAF": {"cosmic_id": "COSM476", "mutation_type": "missense", "tissue": "skin", "somatic_frequency": 0.50},
        "PIK3CA": {"cosmic_id": "COSM775", "mutation_type": "missense", "tissue": "breast", "somatic_frequency": 0.27},
        "ALK": {"cosmic_id": "COSM28055", "mutation_type": "fusion", "tissue": "lung", "somatic_frequency": 0.03}
    }

    @staticmethod
    def annotate_variant(gene, variant_id=None):
        """
        Annotates a specific variant or gene with merged ClinVar and COSMIC data.
        
        Args:
            gene (str): The gene symbol.
            variant_id (str, optional): A specific variant ID. Unused in mock implementation.
            
        Returns:
            dict: Annotated variant dictionary.
        """
        clinvar_data = VariantAnnotator._CLINVAR_DB.get(gene, {})
        cosmic_data = VariantAnnotator._COSMIC_DB.get(gene, {})
        
        clinical_significance = clinvar_data.get("classification", "VUS")
        
        # Evidence level mock logic based on classification
        evidence_level = "C"
        if clinical_significance == "Pathogenic":
            evidence_level = "A"
        elif clinical_significance == "Likely Pathogenic":
            evidence_level = "B"
            
        return {
            "gene": gene,
            "variant_name": clinvar_data.get("variant_name", f"{gene} unknown variant"),
            "hgvsc": clinvar_data.get("hgvsc", "unknown"),
            "clinical_significance": clinical_significance,
            "disease_association": clinvar_data.get("disease", "unknown"),
            "allele_frequency": clinvar_data.get("allele_frequency", 0.0),
            "cosmic_id": cosmic_data.get("cosmic_id", "unknown"),
            "somatic_frequency": cosmic_data.get("somatic_frequency", 0.0),
            "evidence_level": evidence_level,
            "sources": ["ClinVar", "COSMIC"] if clinvar_data and cosmic_data else ["Unknown"]
        }

    @staticmethod
    def annotate_panel(variant_list):
        """
        Annotates a list of variant genes.
        
        Args:
            variant_list (list): List of gene symbol strings.
            
        Returns:
            list: List of annotated variant dictionaries.
        """
        return [VariantAnnotator.annotate_variant(gene) for gene in variant_list]

    @staticmethod
    def classify_pathogenicity(variant):
        """
        Classifies the pathogenicity of a given variant dictionary.
        
        Args:
            variant (dict): Variant dictionary containing 'clinical_significance'.
            
        Returns:
            str: One of 'Pathogenic', 'Likely Pathogenic', 'VUS', 'Likely Benign', 'Benign'.
        """
        sig = variant.get("clinical_significance", "VUS")
        valid_classes = {"Pathogenic", "Likely Pathogenic", "VUS", "Likely Benign", "Benign"}
        if sig in valid_classes:
            return sig
        return "VUS"
