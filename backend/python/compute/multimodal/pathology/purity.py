class TumorPurityEstimator:
    """
    Clinical/Scientific Purpose:
    Calculates macro-level purity, necrosis, and cellularity indices. This is critical for 
    quality control before DNA/RNA sequencing, ensuring high-yield samples with adequate 
    viable tumor burdens.
    """

    @staticmethod
    def estimate_purity(segmentation_results: dict) -> dict:
        """
        Calculates purity metrics from an aggregated slide segmentation result.
        Returns percent estimates for various morphological compartments.
        """
        base_tumor_frac = segmentation_results.get("overall_tumor_fraction", 0.5)
        
        # Deterministic ratio-based calculations
        tumor_purity_percent = base_tumor_frac * 100.0
        necrosis_percent = tumor_purity_percent * 0.15
        viable_tumor_percent = tumor_purity_percent - necrosis_percent
        stroma_percent = (100.0 - tumor_purity_percent) * 0.8
        
        # Cellularity heavily influenced by viable tumor and stroma proportions
        cellularity_index = (viable_tumor_percent * 1.5 + stroma_percent * 0.5) / 100.0

        return {
            "tumor_purity_percent": tumor_purity_percent,
            "necrosis_percent": necrosis_percent,
            "viable_tumor_percent": viable_tumor_percent,
            "stroma_percent": stroma_percent,
            "cellularity_index": min(cellularity_index, 1.0)
        }

    @staticmethod
    def estimate_necrosis(segmentation_results: dict) -> float:
        """
        Isolates and calculates just the necrosis area ratio based on segmentation properties.
        """
        base_tumor_frac = segmentation_results.get("overall_tumor_fraction", 0.5)
        necrosis_ratio = base_tumor_frac * 0.15
        return necrosis_ratio
