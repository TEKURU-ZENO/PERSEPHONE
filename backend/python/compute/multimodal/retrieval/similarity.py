"""
Vector similarity and distance metric module.

Provides fundamental mathematical scoring functions.
"""
import math

class SimilarityScorer:
    """Scorer for computing distances and similarities between vectors."""

    @staticmethod
    def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
        """
        Compute cosine similarity between two vectors.
        
        Args:
            vec_a: First vector.
            vec_b: Second vector.
            
        Returns:
            Cosine similarity score (-1.0 to 1.0).
        """
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
            
        return dot_product / (norm_a * norm_b)

    @staticmethod
    def euclidean_distance(vec_a: list[float], vec_b: list[float]) -> float:
        """
        Compute Euclidean distance between two vectors.
        
        Args:
            vec_a: First vector.
            vec_b: Second vector.
            
        Returns:
            Euclidean distance.
        """
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(vec_a, vec_b)))

    @classmethod
    def batch_similarities(cls, query_vec: list[float], candidate_vecs: list[list[float]]) -> list[dict]:
        """
        Compute similarities between a query and multiple candidates.
        
        Args:
            query_vec: The query vector.
            candidate_vecs: List of candidate vectors to score against.
            
        Returns:
            List of dictionaries with scores.
        """
        results = []
        for i, candidate in enumerate(candidate_vecs):
            results.append({
                "index": i,
                "cosine_sim": cls.cosine_similarity(query_vec, candidate),
                "euclidean_dist": cls.euclidean_distance(query_vec, candidate)
            })
        return results
