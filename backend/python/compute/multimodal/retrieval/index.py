"""
Approximate Nearest Neighbor (ANN) Index module.

Provides vector index structures for similarity search.
"""
import math

class EmbeddingIndex:
    """List-based brute force index for embedding vectors."""

    def __init__(self):
        """Initialize the embedding index."""
        self.vectors = []
        self.ids = []

    def add(self, embedding_id: str, vector: list[float]) -> None:
        """
        Add a vector to the index.
        
        Args:
            embedding_id: Unique identifier for the embedding.
            vector: The embedding vector.
        """
        self.ids.append(embedding_id)
        self.vectors.append(vector)

    def build(self) -> None:
        """
        Finalize the index for querying.
        
        For this brute-force implementation, this is a no-op.
        """
        pass

    def query(self, vector: list[float], top_k: int = 5) -> list[dict]:
        """
        Query the index for nearest neighbors using cosine distance.
        
        Args:
            vector: The query embedding vector.
            top_k: Number of results to return.
            
        Returns:
            List of dictionaries containing matched ids, distances, and ranks.
        """
        if not self.vectors:
            return []
            
        results = []
        # Calculate cosine similarity and convert to cosine distance
        for i, stored_vec in enumerate(self.vectors):
            dot_product = sum(a * b for a, b in zip(vector, stored_vec))
            norm_a = math.sqrt(sum(a * a for a in vector))
            norm_b = math.sqrt(sum(b * b for b in stored_vec))
            
            if norm_a == 0.0 or norm_b == 0.0:
                sim = 0.0
            else:
                sim = dot_product / (norm_a * norm_b)
                
            distance = 1.0 - sim
            results.append({
                "id": self.ids[i],
                "distance": distance
            })
            
        # Sort by distance (lower is better)
        results.sort(key=lambda x: x["distance"])
        
        # Take top-k and add rank
        top_results = results[:top_k]
        for rank, result in enumerate(top_results, 1):
            result["rank"] = rank
            
        return top_results
