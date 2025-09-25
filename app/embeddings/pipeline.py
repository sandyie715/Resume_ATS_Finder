"""
Phase 2: Embeddings & Similarity Matching Pipeline (Industry-Level Robust Version)
"""

from typing import Dict, List, Any, Tuple
from app.embeddings.embedding_model import get_embedding
from app.embeddings.similarity import semantic_skill_analysis
from app.embeddings.experience_check import (
    parse_jd_experience,
    aggregate_resume_experience,
    normalize_skill
)
from app.utils.text_cleaner import preprocess_text
from app.utils.normalizer import normalize_parsed_data
import logging
import numpy as np

logger = logging.getLogger("pipeline")
logger.setLevel(logging.INFO)


# -------------------------
# 1. Compute Experience Similarity
# -------------------------
def compute_experience_similarity(jd_exp: Dict[str, int], resume_exp: Dict[str, int]) -> Tuple[float, List[dict]]:
    total_score = 0
    experience_match_list = []

    if not jd_exp:
        return 0.0, []

    for skill, req_years in jd_exp.items():
        cand_years = resume_exp.get(skill, 0)
        status = "match" if cand_years >= req_years else "insufficient"

        score = min(cand_years / req_years, 1) if req_years > 0 else 0
        total_score += score

        experience_match_list.append({
            "skill": skill,
            "required": req_years,
            "candidate": cand_years,
            "status": status
        })

    avg_score = total_score / len(jd_exp) if len(jd_exp) > 0 else 0
    return round(avg_score, 3), experience_match_list


# -------------------------
# 2. Run Full Similarity Pipeline
# -------------------------
def run_similarity_pipeline(jd_data: Dict[str, Any], resume_data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        # -------------------------
        # Normalize parsed data
        # -------------------------
        jd_data, resume_data = normalize_parsed_data(jd_data, resume_data)

        # -------------------------
        # Extract fields safely
        # -------------------------
        jd_skills: List[str] = [str(s) for s in jd_data.get("skills", []) if s]
        jd_experience: List[str] = [str(e) for e in jd_data.get("experience", []) if e]

        resume_skills: List[str] = [str(s) for s in resume_data.get("Skills", []) if s]
        resume_experience: Dict[str, List[Any]] = resume_data.get("Experience", {}) or {}

        # Normalize skills
        jd_skills_normalized = [normalize_skill(s) for s in jd_skills]
        resume_skills_normalized = [normalize_skill(s) for s in resume_skills]

        # -------------------------
        # Preprocess text for embeddings
        # -------------------------
        jd_text = preprocess_text(" ".join(jd_skills + jd_experience))
        resume_exp_text = " ".join([f"{v[0]} {v[3]}" for _, v in resume_experience.items() if len(v) >= 4])
        resume_text = preprocess_text(" ".join(resume_skills) + " " + resume_exp_text)

        # -------------------------
        # Get embeddings safely
        # -------------------------
        try:
            jd_vector = get_embedding(jd_text)
            resume_vector = get_embedding(resume_text)
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            logger.info(f"JD text: {jd_text}")
            logger.info(f"Resume text: {resume_text}")
            jd_vector = np.zeros((768,))
            resume_vector = np.zeros((768,))

        # -------------------------
        # Skills similarity & missing keywords
        # -------------------------
        skills_sim, missing_keywords = semantic_skill_analysis(jd_skills_normalized, resume_skills_normalized)

        # -------------------------
        # Experience similarity
        # -------------------------
        jd_exp_structured = parse_jd_experience(jd_experience)
        resume_exp_structured = aggregate_resume_experience(resume_experience)
        exp_similarity_score, experience_match = compute_experience_similarity(jd_exp_structured, resume_exp_structured)

        # -------------------------
        # Weighted overall similarity
        # -------------------------
        overall_similarity = round(0.7 * skills_sim + 0.3 * exp_similarity_score, 3)

        # -------------------------
        # Return structured response
        # -------------------------
        return {
            "overall_similarity": overall_similarity,
            "skills_similarity": round(skills_sim, 3),
            "missing_keywords": missing_keywords,
            "experience_match": experience_match
        }

    except Exception as e:
        logger.critical(f"Pipeline failed: {e}", exc_info=True)
        return {
            "overall_similarity": 0.0,
            "skills_similarity": 0.0,
            "missing_keywords": jd_data.get("skills", []),
            "experience_match": []
        }