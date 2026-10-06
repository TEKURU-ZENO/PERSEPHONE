import math

class AttentionRollout:
    """
    Computes attention rollout and overlays to visualize model focus.
    """
    
    @staticmethod
    def compute_attention_map(patch_embeddings, query_embedding=None):
        """
        Computes an attention map based on embeddings.
        
        Args:
            patch_embeddings (list): Embeddings for image patches.
            query_embedding (list, optional): Query embedding for cross-attention.
            
        Returns:
            dict: Attention weights and metrics.
        """
        # Mock softmax normalized scores
        raw_scores = [1.0] * len(patch_embeddings)
        exp_scores = [math.exp(s) for s in raw_scores]
        total_exp = sum(exp_scores)
        attention_weights = [e / total_exp for e in exp_scores] if total_exp > 0 else []
        
        entropy = -sum([w * math.log(w + 1e-9) for w in attention_weights])
        
        return {
            "is_mock": True,
            "attention_weights": attention_weights,
            "entropy": entropy,
            "top_k_indices": list(range(min(5, len(attention_weights)))),
            "coverage_score": 0.85
        }
        
    @staticmethod
    def rollout_visualization(attention_maps):
        """
        Aggregates multiple attention maps for rollout visualization.
        
        Args:
            attention_maps (list): List of attention maps from different layers.
            
        Returns:
            dict: Aggregated attention map and metrics.
        """
        # Mock aggregation
        size = 16
        aggregated_map = [[0.5 for _ in range(size)] for _ in range(size)]
        
        return {
            "is_mock": True,
            "aggregated_map": aggregated_map,
            "layer_count": len(attention_maps),
            "receptive_field_coverage": 0.92
        }
