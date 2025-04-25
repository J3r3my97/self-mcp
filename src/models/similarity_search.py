from typing import Any, Dict, List

import numpy as np

from database.models import Product
from database.repository import FirebaseRepository


class SimilaritySearch:
    def __init__(self, repository: FirebaseRepository):
        self.repository = repository

    async def search(
        self, query_embedding: List[float], top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for similar products using cosine similarity."""
        # Get all products from the database
        products = await self.repository.search_products({})

        # Calculate similarities
        similarities = []
        for product in products:
            # Get product embedding from storage
            embedding = await self._get_product_embedding(product.id)
            if embedding is None:
                continue

            # Calculate cosine similarity
            similarity = self._cosine_similarity(query_embedding, embedding)
            similarities.append({"product": product, "similarity": float(similarity)})

        # Sort by similarity and return top-k results
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        return similarities[:top_k]

    async def _get_product_embedding(self, product_id: str) -> List[float]:
        """Get product embedding from storage."""
        return await self.repository.get_embedding(product_id)

    async def save_product_embedding(
        self, product_id: str, embedding: List[float]
    ) -> str:
        """Save product embedding to storage."""
        return await self.repository.upload_embedding(product_id, embedding)

    def _cosine_similarity(self, emb1: List[float], emb2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings."""
        emb1 = np.array(emb1)
        emb2 = np.array(emb2)

        # Ensure embeddings have the same dimension
        min_dim = min(emb1.shape[0], emb2.shape[0])
        emb1 = emb1[:min_dim]
        emb2 = emb2[:min_dim]

        # Normalize embeddings
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        emb1_normalized = emb1 / norm1
        emb2_normalized = emb2 / norm2

        # Calculate cosine similarity
        similarity = np.dot(emb1_normalized, emb2_normalized)

        # Ensure the result is in [0,1] range
        return float(max(0.0, min(1.0, similarity)))
