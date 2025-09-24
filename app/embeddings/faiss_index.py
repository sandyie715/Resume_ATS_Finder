"""
FAISS index utility for Phase 2
Used for fast vector similarity search for skills/resumes
"""

import faiss
import numpy as np

class FaissIndex:
    def __init__(self, dim: int):
        """
        Initialize a FAISS index for cosine similarity
        Args:
            dim (int): Dimension of embeddings
        """
        # Use IndexFlatIP for inner product (cosine similarity after normalization)
        self.index = faiss.IndexFlatIP(dim)
        self.vectors = []
        self.ids = []

    def add_vectors(self, vectors: np.ndarray, ids: list):
        """
        Add vectors to the index
        Args:
            vectors (np.ndarray): normalized vectors, shape (N, dim)
            ids (list): list of IDs corresponding to vectors
        """
        self.vectors.extend(vectors)
        self.ids.extend(ids)
        self.index.add(np.array(vectors).astype('float32'))

    def search(self, query_vector: np.ndarray, top_k: int = 5):
        """
        Search top-k most similar vectors
        Args:
            query_vector (np.ndarray): normalized query vector
            top_k (int): number of results to return

        Returns:
            list of tuples (id, similarity_score)
        """
        query_vector = np.array([query_vector]).astype('float32')
        distances, indices = self.index.search(query_vector, top_k)
        results = []
        for idx, score in zip(indices[0], distances[0]):
            if idx < len(self.ids):
                results.append((self.ids[idx], float(score)))
        return results