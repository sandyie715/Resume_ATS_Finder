"""
Phase 2: Embeddings & Similarity Matching Pipeline
This module orchestrates the JD ↔ Resume similarity workflow.
Includes FAISS skills similarity and experience parsing.
"""

from typing import Dict, List, Any
from app.embeddings.embedding_model import get_embedding
from app.embeddings.similarity import (
    compute_overall_similarity,
    compute_skills_similarity,
    find_missing_keywords,
    match_experience
)
from app.utils.text_cleaner import preprocess_text


def run_similarity_pipeline(jd_data: Dict[str, Any], resume_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point for Phase 2 similarity matching.

    Args:
        jd_data (dict): Parsed JD JSON containing 'skills' and 'experience'.
        resume_data (dict): Parsed Resume JSON containing 'Skills' and 'Experience'.

    Returns:
        dict: {
            "overall_similarity": float,       # Cosine similarity between JD & Resume embeddings
            "skills_similarity": float,        # FAISS-based skill similarity score
            "missing_keywords": List[str],     # Skills in JD not found in Resume
            "experience_match": List[dict]     # Experience comparison per skill
        }
    """

    # -------------------------
    # 1. Extract fields
    # -------------------------
    jd_skills: List[str] = jd_data.get("skills", [])
    jd_experience: List[str] = jd_data.get("experience", [])

    resume_skills: List[str] = resume_data.get("Skills", [])
    resume_experience: Dict[str, List[Any]] = resume_data.get("Experience", {})

    # -------------------------
    # 2. Preprocess text
    # -------------------------
    jd_text: str = preprocess_text(" ".join(jd_skills + jd_experience))
    
    # Flatten resume experience → "role years" format for embedding
    resume_exp_text: str = " ".join([f"{v[0]} {v[3]}" for _, v in resume_experience.items()])
    resume_text: str = preprocess_text(" ".join(resume_skills) + " " + resume_exp_text)

    # -------------------------
    # 3. Get embeddings
    # -------------------------
    jd_vector = get_embedding(jd_text)
    resume_vector = get_embedding(resume_text)

    # -------------------------
    # 4. Compute similarities
    # -------------------------
    overall_sim = compute_overall_similarity(jd_vector, resume_vector)
    skills_sim = compute_skills_similarity(jd_skills, resume_skills)

    # -------------------------
    # 5. Find missing keywords
    # -------------------------
    missing_keywords: List[str] = find_missing_keywords(jd_skills, resume_skills)

    # -------------------------
    # 6. Match experience
    # -------------------------
    experience_match: List[dict] = match_experience(jd_experience, resume_experience)

    # -------------------------
    # 7. Prepare and return response
    # -------------------------
    return {
        "overall_similarity": round(overall_sim, 3),
        "skills_similarity": round(skills_sim, 3),
        "missing_keywords": missing_keywords,
        "experience_match": experience_match
    }