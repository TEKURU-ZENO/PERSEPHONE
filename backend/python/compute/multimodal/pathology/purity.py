class TumorPurityEstimator:
    """
    Clinical/Scientific Purpose:
    Calculates macro-level purity, necrosis, and cellularity indices. This is critical for 
    quality control before DNA/RNA sequencing, ensuring high-yield samples with adequate 
    viable tumor burdens.

    IMPORTANT CLINICAL INVARIANT:
    Tumor purity, necrosis, and stroma are independent biological and morphological measurements
    derived from multi-class tissue segmentation masks. They MUST NOT be calculated as fixed 
    fractional multipliers of each other (e.g. necrosis != tumor * 0.15; stroma != (100 - tumor) * 0.8).
    Each compartment must be independently quantified from segmentation masks or explicit inputs.
    """

    @staticmethod
    def estimate_purity(segmentation_results: dict) -> dict:
        """
        Calculates purity metrics from independent morphological measurements or segmentation results.

        Args:
            segmentation_results (dict): Dictionary containing independent compartment measurements:
                - 'tumor_purity_percent' or 'overall_tumor_fraction' / 'tumor_fraction'
                - 'necrosis_percent' or 'necrosis_fraction' (independent measurement)
                - 'stroma_percent' or 'stroma_fraction' (independent measurement)

        Returns percent estimates for each distinct morphological compartment.
        """
        # 1. Independent Tumor Quantification (supports tumor_area_percent or tumor_purity_percent)
        if "tumor_area_percent" in segmentation_results:
            tumor_purity_percent = float(segmentation_results["tumor_area_percent"])
        elif "tumor_purity_percent" in segmentation_results:
            tumor_purity_percent = float(segmentation_results["tumor_purity_percent"])
        else:
            base_tumor_frac = segmentation_results.get("overall_tumor_fraction", segmentation_results.get("tumor_fraction", 0.0))
            tumor_purity_percent = float(base_tumor_frac) * 100.0 if base_tumor_frac <= 1.0 else float(base_tumor_frac)

        # 2. Independent Necrosis Quantification (NOT derived via fixed multiplier)
        if "necrosis_percent" in segmentation_results:
            necrosis_percent = float(segmentation_results["necrosis_percent"])
        elif "necrosis_fraction" in segmentation_results:
            necrosis_percent = float(segmentation_results["necrosis_fraction"]) * 100.0
        else:
            necrosis_percent = 0.0

        # 3. Independent Stroma Quantification (NOT derived via fixed multiplier)
        if "stroma_percent" in segmentation_results:
            stroma_percent = float(segmentation_results["stroma_percent"])
        elif "stroma_fraction" in segmentation_results:
            stroma_percent = float(segmentation_results["stroma_fraction"]) * 100.0
        else:
            stroma_percent = 0.0

        # Viable tumor is tumor minus non-viable necrotic tumor tissue within the tumor bed
        viable_tumor_percent = max(0.0, tumor_purity_percent - necrosis_percent)

        # Cellularity index based on independent viable cellular compartments
        cellularity_index = min(1.0, max(0.0, (viable_tumor_percent * 1.5 + stroma_percent * 0.5) / 100.0))

        return {
            "tumor_area_percent": round(tumor_purity_percent, 2),
            "tumor_purity_percent": round(tumor_purity_percent, 2),
            "necrosis_percent": round(necrosis_percent, 2),
            "viable_tumor_percent": round(viable_tumor_percent, 2),
            "stroma_percent": round(stroma_percent, 2),
            "cellularity_index": round(cellularity_index, 4)
        }

    @staticmethod
    def estimate_necrosis(segmentation_results: dict) -> float:
        """
        Isolates and calculates just the necrosis area ratio based on independent segmentation properties.
        """
        if "necrosis_fraction" in segmentation_results:
            return float(segmentation_results["necrosis_fraction"])
        if "necrosis_percent" in segmentation_results:
            return float(segmentation_results["necrosis_percent"]) / 100.0
        return 0.0
