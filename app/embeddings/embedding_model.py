# """
# Embedding Model Loader for Phase 2
# Uses Sentence-Transformers (all-MiniLM-L6-v2).
# """

# from sentence_transformers import SentenceTransformer
# import numpy as np

# # -------------------------
# # 1. Load Model (Singleton)
# # -------------------------
# _model = None

# def load_model():
#     """
#     Lazy-loads the sentence transformer model.
#     Ensures we don’t reload multiple times.
#     """
#     global _model
#     if _model is None:
#         _model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
#     return _model


# # -------------------------
# # 2. Get Embedding
# # -------------------------
# def get_embedding(text: str) -> np.ndarray:
#     """
#     Generate embedding vector for given text.

#     Args:
#         text (str): Input text

#     Returns:
#         np.ndarray: Normalized embedding vector
#     """
#     model = load_model()
#     embedding = model.encode(text, convert_to_numpy=True)
#     # Normalize to unit vector (important for cosine similarity)
#     return embedding / np.linalg.norm(embedding)

"""
Embedding Model Loader for Phase 2 (Industry-Grade)
Uses BAAI/bge-base-en-v1.5 for high-accuracy semantic similarity.
"""

from sentence_transformers import SentenceTransformer
import numpy as np

# -------------------------
# 1. Load Model (Singleton)
# -------------------------
_model = None

def load_model():
    """
    Lazy-loads the sentence transformer model.
    Ensures we don’t reload multiple times.
    """
    global _model
    if _model is None:
        # 🚀 Using a stronger semantic model (768-dim) for better similarity
        _model = SentenceTransformer("BAAI/bge-base-en-v1.5")
    return _model


# -------------------------
# 2. Get Embedding
# -------------------------
def get_embedding(text: str) -> np.ndarray:
    """
    Generate normalized embedding vector for given text.
    Handles empty strings gracefully.

    Args:
        text (str): Input text

    Returns:
        np.ndarray: Normalized embedding vector
    """
    if not text or not text.strip():
        return np.zeros(768)  # BGE base dimension

    model = load_model()
    embedding = model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
    return embedding
