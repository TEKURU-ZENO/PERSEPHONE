class MutationSignatureClassifier:
    """
    Classifies mutation signatures and computes mutational burden (TMB) 
    and microsatellite instability (MSI) scores for a patient profile.
    """

    @staticmethod
    def classify_signature(mutation_profile):
        """
        Infers the dominant mutational signature based on affected genes.
        
        Args:
            mutation_profile (dict): Dictionary with 'genes' list and optionally 'mutation_types'.
            
        Returns:
            dict: Signature classification details.
        """
        genes = set(mutation_profile.get("genes", []))
        
        hr_genes = {"BRCA1", "BRCA2", "PALB2", "RAD51"}
        mmr_genes = {"MLH1", "MSH2", "MSH6", "PMS2"}
        
        dominant_signature = "SBS1 (Aging)"
        confidence = 0.5
        contributing_signatures = [{"name": "SBS1", "weight": 1.0}]
        
        if genes.intersection(hr_genes):
            dominant_signature = "SBS3 (HRD)"
            confidence = 0.9
            contributing_signatures = [
                {"name": "SBS3", "weight": 0.8},
                {"name": "SBS1", "weight": 0.2}
            ]
        elif genes.intersection(mmr_genes):
            dominant_signature = "SBS6 (MMR Deficiency)"
            confidence = 0.85
            contributing_signatures = [
                {"name": "SBS6", "weight": 0.9},
                {"name": "SBS1", "weight": 0.1}
            ]
        elif "BRAF" in genes:
            dominant_signature = "SBS7 (UV)"
            confidence = 0.7
            contributing_signatures = [
                {"name": "SBS7", "weight": 0.7},
                {"name": "SBS1", "weight": 0.3}
            ]
            
        return {
            "dominant_signature": dominant_signature,
            "confidence": confidence,
            "contributing_signatures": contributing_signatures
        }

    @staticmethod
    def compute_tmb(variant_count, exome_size_mb=30.0):
        """
        Computes Tumor Mutational Burden (TMB).
        
        Args:
            variant_count (int): Total number of somatic variants.
            exome_size_mb (float): Exome size in megabases.
            
        Returns:
            dict: Contains tmb_score and tmb_status.
        """
        tmb_score = variant_count / exome_size_mb
        
        if tmb_score >= 10.0:
            status = "TMB-High"
        elif tmb_score >= 6.0:
            status = "TMB-Intermediate"
        else:
            status = "TMB-Low"
            
        return {
            "tmb_score": round(tmb_score, 2),
            "tmb_status": status
        }

    @staticmethod
    def compute_msi_score(microsatellite_loci):
        """
        Computes Microsatellite Instability (MSI) score.
        
        Args:
            microsatellite_loci (list): List of dicts with 'locus' and 'stable' (bool).
            
        Returns:
            dict: MSI metrics including msi_score and msi_status.
        """
        if not microsatellite_loci:
            return {
                "msi_score": 0.0,
                "msi_status": "MSS",
                "unstable_loci_count": 0,
                "total_loci": 0
            }
            
        total_loci = len(microsatellite_loci)
        unstable_count = sum(1 for locus in microsatellite_loci if not locus.get("stable", True))
        
        msi_score = unstable_count / total_loci
        status = "MSI-H" if msi_score >= 0.3 else "MSS"
        
        return {
            "msi_score": round(msi_score, 3),
            "msi_status": status,
            "unstable_loci_count": unstable_count,
            "total_loci": total_loci
        }
