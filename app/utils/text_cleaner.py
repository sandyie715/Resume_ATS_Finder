"""
Utility functions for text preprocessing.
Phase 2 requires clean text before embeddings.
"""

import re
import string
from typing import List


# -------------------------
# 1. Stopwords (basic set)
# -------------------------
STOPWORDS = {
    "a", "an", "the", "is", "are", "in", "on", "at", "to", "for", "with",
    "of", "and", "or", "by", "from", "as", "this", "that", "it", "be"
}


# -------------------------
# 2. Preprocessing pipeline
# -------------------------
def preprocess_text(text: str) -> str:
    """
    Preprocess input text: lowercase, remove punctuation,
    remove stopwords, normalize spaces.

    Args:
        text (str): raw input text

    Returns:
        str: cleaned text
    """
    if not text:
        return ""

    # Lowercase
    text = text.lower()

    # Remove punctuation
    text = text.translate(str.maketrans("", "", string.punctuation))

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    # Tokenize & remove stopwords
    tokens = [t for t in text.split() if t not in STOPWORDS]

    return " ".join(tokens)


def preprocess_list(items: List[str]) -> List[str]:
    """
    Preprocess a list of text strings.

    Args:
        items (list[str]): list of text values

    Returns:
        list[str]: cleaned values
    """
    return [preprocess_text(i) for i in items if i]