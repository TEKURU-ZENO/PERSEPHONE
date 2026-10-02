"""
PERSEPHONE Genomic Variant Annotator.
Enforces variant-level precision with mandatory HGVS coding nomenclature (hgvsc).
Separates germline classification (ClinVar/ACMG) from somatic actionability (AMP/ASCO/CAP Tiers).
"""

class VariantAnnotator:
    """
    Annotates genomic variants with clinical germline and somatic actionability significance.
    Combines ClinVar (germline ACMG) and AMP/ASCO/CAP (somatic actionability) standards.
    """

    _CLINVAR_DB = {
        ("BRCA1", "c.1961delA"): {
            "variation_id": "VCV000055474",
            "variant_name": "BRCA1 c.1961delA (p.Glu654Glyfs*14)",
            "hgvsc": "c.1961delA",
            "protein_change": "p.Glu654Glyfs*14",
            "consequence": "Frameshift leading to Homologous Recombination Deficiency (HRD)",
            "germline_classification": "Pathogenic",
            "germline_disease": "Hereditary Breast and Ovarian Cancer syndrome",
            "gnomad_af": 0.00003,
            "somatic_tier": "Tier I-A",
            "evidence_level": "A",
            "therapeutic_implications": "FDA-approved PARP inhibitors (olaparib, niraparib, rucaparib)",
            "somatic_disease": "High-grade serous ovarian carcinoma, breast cancer"
        },
        ("EGFR", "c.2573T>G"): {
            "variation_id": "VCV000016618",
            "variant_name": "EGFR c.2573T>G (p.Leu858Arg)",
            "hgvsc": "c.2573T>G",
            "protein_change": "p.Leu858Arg",
            "consequence": "Exon 21 missense activating kinase domain",
            "germline_classification": "Likely Benign",
            "germline_disease": "N/A",
            "gnomad_af": None,
            "somatic_tier": "Tier I-A",
            "evidence_level": "A",
            "therapeutic_implications": "FDA-approved EGFR TKIs (osimertinib preferred per FLAURA)",
            "somatic_disease": "Non-small cell lung cancer"
        },
        ("EGFR", "c.2369C>T"): {
            "variation_id": "VCV000016620",
            "variant_name": "EGFR c.2369C>T (p.Thr790Met)",
            "hgvsc": "c.2369C>T",
            "protein_change": "p.Thr790Met",
            "consequence": "Exon 20 gatekeeper resistance alteration",
            "germline_classification": "Uncertain Significance",
            "germline_disease": "Hereditary lung cancer susceptibility (rare)",
            "gnomad_af": None,
            "somatic_tier": "Tier I-A",
            "evidence_level": "A",
            "therapeutic_implications": "Third-generation EGFR TKI (osimertinib) post-first/second generation TKI progression",
            "somatic_disease": "Non-small cell lung cancer"
        },
        ("KRAS", "c.35G>A"): {
            "variation_id": "VCV000012574",
            "variant_name": "KRAS c.35G>A (p.Gly12Asp)",
            "hgvsc": "c.35G>A",
            "protein_change": "p.Gly12Asp",
            "consequence": "Codon 12 hotspot mutation trapping GTP-bound active state",
            "germline_classification": "Pathogenic",
            "germline_disease": "RASopathy / Cardiofaciocutaneous syndrome (germline)",
            "gnomad_af": None,
            "somatic_tier": "Tier III (unknown clinical significance)",
            "evidence_level": "D",
            "therapeutic_implications": "No approved targeted inhibitor; continue standard chemotherapy; evaluate investigational G12D/pan-RAS clinical trials",
            "somatic_disease": "Colorectal adenocarcinoma, pancreatic cancer"
        },
        ("KRAS", "c.34G>T"): {
            "variation_id": "VCV000012582",
            "variant_name": "KRAS c.34G>T (p.Gly12Cys)",
            "hgvsc": "c.34G>T",
            "protein_change": "p.Gly12Cys",
            "consequence": "Codon 12 cysteine substitution susceptible to covalent inhibition",
            "germline_classification": "Uncertain Significance",
            "germline_disease": "N/A",
            "gnomad_af": None,
            "somatic_tier": "Tier I-A",
            "evidence_level": "A",
            "therapeutic_implications": "FDA-approved covalent G12C inhibitors (adagrasib, sotorasib; ± cetuximab in CRC)",
            "somatic_disease": "Non-small cell lung cancer, colorectal cancer"
        },
        ("TP53", "c.524G>A"): {
            "variation_id": "VCV000012356",
            "variant_name": "TP53 c.524G>A (p.Arg175His)",
            "hgvsc": "c.524G>A",
            "protein_change": "p.Arg175His",
            "consequence": "Conformational DNA-binding domain hotspot abolishing wild-type transactivation",
            "germline_classification": "Pathogenic",
            "germline_disease": "Li-Fraumeni syndrome (germline only)",
            "gnomad_af": None,
            "somatic_tier": "Tier II-C",
            "evidence_level": "C",
            "therapeutic_implications": "Adverse prognostic marker; consider immunotherapy if TMB-High; clinical trials for p53 reactivation",
            "somatic_disease": "Solid tumors (ovarian, breast, lung, colorectal)"
        },
        ("BRAF", "c.1799T>A"): {
            "variation_id": "VCV000013959",
            "variant_name": "BRAF c.1799T>A (p.Val600Glu)",
            "hgvsc": "c.1799T>A",
            "protein_change": "p.Val600Glu",
            "consequence": "Monomeric constitutive kinase activation in activation segment",
            "germline_classification": "Pathogenic",
            "germline_disease": "Cardiofaciocutaneous syndrome (germline)",
            "gnomad_af": None,
            "somatic_tier": "Tier I-A",
            "evidence_level": "A",
            "therapeutic_implications": "FDA-approved BRAF + MEK inhibitor combination (dabrafenib + trametinib, encorafenib + cetuximab)",
            "somatic_disease": "Melanoma, colorectal cancer, NSCLC"
        },
        ("PIK3CA", "c.3140A>G"): {
            "variation_id": "VCV000017690",
            "variant_name": "PIK3CA c.3140A>G (p.His1047Arg)",
            "hgvsc": "c.3140A>G",
            "protein_change": "p.His1047Arg",
            "consequence": "Kinase domain hotspot hyperactivating PI3K-AKT signaling",
            "germline_classification": "Pathogenic",
            "germline_disease": "PIK3CA-related overgrowth spectrum (PROS)",
            "gnomad_af": None,
            "somatic_tier": "Tier I-B",
            "evidence_level": "B",
            "therapeutic_implications": "FDA-approved PI3K alpha-selective inhibitor (alpelisib)",
            "somatic_disease": "HR+/HER2- metastatic breast cancer"
        },
        ("ALK", "fusion"): {
            "variation_id": "VCV000030711",
            "variant_name": "EML4-ALK fusion",
            "hgvsc": "fusion",
            "protein_change": "EML4-ALK fusion",
            "consequence": "Constitutive ALK kinase activation via chromosomal inversion/fusion",
            "germline_classification": "N/A",
            "germline_disease": "N/A",
            "gnomad_af": None,
            "somatic_tier": "Tier I-A",
            "evidence_level": "A",
            "therapeutic_implications": "FDA-approved ALK TKIs (alectinib, brigatinib, lorlatinib)",
            "somatic_disease": "Non-small cell lung cancer"
        }
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
    def annotate_variant(gene: str, hgvsc: str) -> dict:
        """
        Annotates a specific variant using strictly required gene and hgvsc coordinates.
        
        Args:
            gene (str): Gene symbol (e.g. 'BRCA1', 'KRAS', 'EGFR').
            hgvsc (str): HGVS coding sequence nomenclature (e.g. 'c.1961delA', 'c.35G>A').
            
        Returns:
            dict: Annotated variant with distinct germline_assessment and somatic_actionability blocks.
        """
        key = (gene, hgvsc)
        record = VariantAnnotator._CLINVAR_DB.get(key)
        cosmic_data = VariantAnnotator._COSMIC_DB.get(gene, {})

        if record:
            germline = {
                "classification": record["germline_classification"],
                "disease": record["germline_disease"],
                "gnomad_af": record["gnomad_af"]
            }
            somatic = {
                "tier": record["somatic_tier"],
                "evidence_level": record["evidence_level"],
                "therapeutic_implications": record["therapeutic_implications"],
                "disease": record["somatic_disease"]
            }
            variant_name = record["variant_name"]
            consequence = record["consequence"]
            clinical_sig = record["germline_classification"]
            disease_assoc = record["somatic_disease"]
            evidence_level = record["evidence_level"]
        else:
            germline = {
                "classification": "VUS",
                "disease": "unknown",
                "gnomad_af": None
            }
            somatic = {
                "tier": "Tier III (unknown clinical significance)",
                "evidence_level": "D",
                "therapeutic_implications": "No approved targeted therapy; clinical trial consideration",
                "disease": "Solid tumor"
            }
            variant_name = f"{gene} {hgvsc}"
            consequence = "Unknown coding alteration"
            clinical_sig = "VUS"
            disease_assoc = "unknown"
            evidence_level = "D"

        return {
            "gene": gene,
            "hgvsc": hgvsc,
            "variant_name": variant_name,
            "consequence": consequence,
            "clinical_significance": clinical_sig,
            "disease_association": disease_assoc,
            "evidence_level": evidence_level,
            "actionability_tier": somatic["tier"],
            "germline_assessment": germline,
            "somatic_actionability": somatic,
            "cosmic_id": cosmic_data.get("cosmic_id", "unknown"),
            "somatic_frequency": cosmic_data.get("somatic_frequency", 0.0),
            "sources": ["ClinVar", "COSMIC"] if record and cosmic_data else ["Unknown"]
        }

    @staticmethod
    def annotate_panel(variant_list: list) -> list:
        """
        Annotates a list of variant descriptors.
        
        Args:
            variant_list (list): List of dicts (with 'gene' and 'hgvsc') or (gene, hgvsc) tuples.
            
        Returns:
            list: List of annotated variant dictionaries.
        """
        annotated = []
        for item in variant_list:
            if isinstance(item, dict):
                g = item.get("gene", "")
                h = item.get("hgvsc") or item.get("variant", "")
                annotated.append(VariantAnnotator.annotate_variant(g, h))
            elif isinstance(item, (list, tuple)) and len(item) == 2:
                annotated.append(VariantAnnotator.annotate_variant(item[0], item[1]))
            else:
                raise ValueError("Items in variant_list must be dicts with 'gene' and 'hgvsc' or (gene, hgvsc) tuples")
        return annotated

    @staticmethod
    def classify_pathogenicity(variant: dict) -> str:
        """
        Classifies the pathogenicity of a variant dictionary.
        
        Args:
            variant (dict): Variant dictionary containing 'germline_assessment' or 'clinical_significance'.
            
        Returns:
            str: ACMG classification category.
        """
        germline = variant.get("germline_assessment", {})
        sig = germline.get("classification") or variant.get("clinical_significance", "VUS")
        valid_classes = {"Pathogenic", "Likely Pathogenic", "VUS", "Likely Benign", "Benign"}
        if sig in valid_classes:
            return sig
        return "VUS"
