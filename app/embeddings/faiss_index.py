"""
FAISS Index Utility – Industry-Grade Version
Used for fast vector similarity search (skills, resumes, experience) in Phase 2.
"""

import faiss
import numpy as np


class FaissIndex:
    def __init__(self, dim: int = 768):
        """
        Initialize a FAISS index for cosine similarity search.

        Args:
            dim (int): Dimension of embeddings (default: 768 for BGE-base)
        """
        self.dim = dim
        # FAISS IndexFlatIP = Inner Product (cosine similarity after normalization)
        self.index = faiss.IndexFlatIP(self.dim)
        self.vectors = []
        self.ids = []

    # -------------------------
    # Add vectors to index
    # -------------------------
    def add_vectors(self, vectors: np.ndarray, ids: list):
        """
        Add normalized vectors to the FAISS index.

        Args:
            vectors (np.ndarray): Embedding vectors (N, dim)
            ids (list): Identifiers corresponding to each vector

        Raises:
            ValueError: If dimensions mismatch or data is invalid
        """
        vectors = np.array(vectors, dtype=np.float32)

        if vectors.ndim != 2 or vectors.shape[1] != self.dim:
            raise ValueError(
                f"[FAISS ERROR] Expected shape (N, {self.dim}), got {vectors.shape}"
            )

        # Normalize for cosine similarity
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        vectors = vectors / np.clip(norms, a_min=1e-10, a_max=None)

        self.vectors.extend(vectors)
        self.ids.extend(ids)
        self.index.add(vectors)

    # -------------------------
    # Search top-k matches
    # -------------------------
    def search(self, query_vector: np.ndarray, top_k: int = 5):
        """
        Search top-k most similar vectors from the index.

        Args:
            query_vector (np.ndarray): Normalized query embedding (dim,)
            top_k (int): Number of results to return

        Returns:
            list[tuple]: List of (id, similarity_score) pairs sorted by similarity
        """
        query_vector = np.array(query_vector, dtype=np.float32).reshape(1, -1)

        if query_vector.shape[1] != self.dim:
            raise ValueError(
                f"[FAISS ERROR] Query vector dimension mismatch. Expected {self.dim}, got {query_vector.shape[1]}"
            )

        # Normalize query for cosine similarity
        query_vector = query_vector / np.clip(
            np.linalg.norm(query_vector, axis=1, keepdims=True), a_min=1e-10, a_max=None
        )

        distances, indices = self.index.search(query_vector, top_k)
        results = []

        for idx, score in zip(indices[0], distances[0]):
            if idx < len(self.ids):
                results.append((self.ids[idx], float(score)))

        return results

    # -------------------------
    # Reset index (optional utility)
    # -------------------------
    def reset(self):
        """
        Clears the index and resets all stored vectors & IDs.
        Useful during testing or model updates.
        """
        self.index = faiss.IndexFlatIP(self.dim)
        self.vectors.clear()
        self.ids.clear()