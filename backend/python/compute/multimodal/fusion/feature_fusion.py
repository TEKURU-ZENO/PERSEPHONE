class FeatureFusionEngine:
    """
    Engine for fusing multimodal features, specifically image and genomic data.
    Provides methods for multimodal data integration and updating digital twin simulations.
    """
    
    @staticmethod
    def fuse_image_genomic(image_features, genomic_features):
        """
        Fuses image features and genomic features into a single representation.
        
        Args:
            image_features (dict or list): Features extracted from images.
            genomic_features (dict or list): Features from genomic data.
            
        Returns:
            dict: Fusion results containing fused vector and feature dimensions.
        """
        # Normalize inputs: extract numeric values from dicts
        if isinstance(image_features, dict):
            img_vals = [float(v) for v in image_features.values() if isinstance(v, (int, float))]
        else:
            img_vals = list(image_features)

        if isinstance(genomic_features, dict):
            gen_vals = [float(v) for v in genomic_features.values() if isinstance(v, (int, float))]
        else:
            gen_vals = list(genomic_features)

        # Weighted fusion: concatenate then average where dimensions align
        if len(img_vals) == len(gen_vals):
            fused_vector = [i * 0.6 + g * 0.4 for i, g in zip(img_vals, gen_vals)]
        else:
            fused_vector = img_vals + gen_vals

        return {
            "fused_vector": fused_vector,
            "image_weight": 0.6,
            "genomic_weight": 0.4,
            "fusion_method": "weighted_concatenation",
            "feature_dim": len(fused_vector)
        }
        
    @staticmethod
    def update_digital_twin_params(purity_data, current_params=None):
        """
        Updates digital twin simulation parameters based on tumor purity data.
        
        Args:
            purity_data (dict): Dictionary containing purity and related metrics.
            current_params (dict, optional): Existing simulation parameters.
            
        Returns:
            dict: Updated simulation parameters.
        """
        params = current_params or {
            "carrying_capacity_K": 10000.0,
            "growth_rate_alpha": 0.05,
            "resistant_fraction": 0.1
        }
        
        purity = purity_data.get("purity", 50.0)
        mitosis = purity_data.get("mitosis_rate", 0.0)
        lymphocyte_density = purity_data.get("lymphocyte_density", 0.0)
        
        k_base = 10000.0
        k_new = k_base * (purity / 100.0)
        alpha_new = params["growth_rate_alpha"] * (1.0 + mitosis)
        resistant_new = params["resistant_fraction"] * (1.0 - lymphocyte_density * 0.5)
        
        return {
            "carrying_capacity_K": k_new,
            "growth_rate_alpha": alpha_new,
            "resistant_fraction": max(0.0, resistant_new),
            "updated_fields": ["carrying_capacity_K", "growth_rate_alpha", "resistant_fraction"]
        }
        
    @staticmethod
    def compute_attention_weights(image_features, clinical_context=None):
        """
        Computes attention weights for image features, potentially guided by clinical context.
        
        Args:
            image_features (list): Input feature vector.
            clinical_context (dict, optional): Additional clinical context.
            
        Returns:
            dict: Feature importance weights.
        """
        weights = [abs(f) / (sum([abs(x) for x in image_features]) + 1e-6) for f in image_features]
        return {
            "attention_weights": weights,
            "context_applied": clinical_context is not None,
            "num_features": len(image_features)
        }
