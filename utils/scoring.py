# utils/scoring.py
import json
from utils.similarity import jd_resume_similarity

def calculate_match_score(combined_json_path="combined_output.json",
                          weight_similarity=0.6,
                          weight_keywords=0.4):
    """
    Calculate final ATS match score by combining:
    - Semantic similarity (Sentence-Transformers embeddings)
    - Keyword overlap (JD skills vs Resume skills)
    
    Args:
        combined_json_path: Path to combined resume + JD JSON
        weight_similarity: Weight for semantic similarity (default 0.6)
        weight_keywords: Weight for keyword overlap (default 0.4)

    Returns:
        dict with breakdown and final score
    """
    # Get Phase 2 results (similarity + missing keywords)
    sim_results = jd_resume_similarity(combined_json_path)

    overall_similarity = sim_results.get("overall_similarity", 0.0)
    matched_skills = sim_results.get("matched_skills", [])
    missing_skills = sim_results.get("missing_skills", [])

    # Keyword overlap ratio
    jd_total = len(matched_skills) + len(missing_skills)
    keyword_score = (len(matched_skills) / jd_total) if jd_total > 0 else 0.0

    # Weighted final score
    final_score = (weight_similarity * overall_similarity) + \
                  (weight_keywords * keyword_score)

    return {
        "overall_similarity": round(overall_similarity, 3),
        "keyword_overlap": round(keyword_score, 3),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "final_match_score": round(final_score, 3),
        "weights": {
            "similarity": weight_similarity,
            "keywords": weight_keywords
        }
    }
