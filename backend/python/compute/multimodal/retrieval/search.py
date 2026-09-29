"""
Search engine module for pathology slides.

Provides embedding-based retrieval functionality.
"""
from backend.python.compute.multimodal.retrieval.index import EmbeddingIndex

class SlideSearchEngine:
    """Search engine for finding similar pathology slides."""

    def __init__(self):
        """Initialize the slide search engine with an embedding index."""
        self.index = EmbeddingIndex()
        self.embedding_dim = None

    def index_slide(self, slide_id: str, embedding_vector: list[float]) -> None:
        """
        Add a slide's embedding to the search index.
        
        Args:
            slide_id: Unique identifier for the slide.
            embedding_vector: The embedding representation of the slide.
        """
        if self.embedding_dim is None:
            self.embedding_dim = len(embedding_vector)
            
        self.index.add(slide_id, embedding_vector)

    def search(self, query_embedding: list[float], top_k: int = 5) -> dict:
        """
        Search for similar slides given a query embedding.
        
        Args:
            query_embedding: The embedding to search for.
            top_k: Maximum number of results to return.
            
        Returns:
            Dictionary containing search results and metadata.
        """
        results = self.index.query(query_embedding, top_k=top_k)
        
        # Transform index results to expected output format
        matches = []
        for res in results:
            matches.append({
                "slide_id": res["id"],
                "similarity_score": 1.0 - res["distance"], # Convert distance back to similarity
                "rank": res["rank"]
            })
            
        return {
            "query_dim": len(query_embedding),
            "top_k": top_k,
            "matches": matches
        }

    def get_index_stats(self) -> dict:
        """
        Retrieve statistics about the current index.
        
        Returns:
            Dictionary of index statistics.
        """
        return {
            "total_indexed": len(self.index.vectors),
            "embedding_dim": self.embedding_dim or 0
        }
