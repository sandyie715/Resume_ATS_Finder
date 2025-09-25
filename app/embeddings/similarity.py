"""
Similarity utilities for Phase 2 (Industry-level - Step 6)
- Weighted overall similarity (skills + experience)
- Skills similarity (FAISS-based)
- Missing keyword detection
- Experience parsing & matching
"""

import re
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Tuple, Dict
from app.embeddings.embedding_model import get_embedding
import logging

logger = logging.getLogger("similarity")
logger.setLevel(logging.INFO)


# -------------------------
# 1. Overall Similarity
# -------------------------
def compute_overall_similarity(skills_similarity: float, experience_match: List[Dict], exp_weight: float = 0.3) -> float:
    """
    Compute weighted overall similarity using skills similarity and experience match.

    Args:
        skills_similarity (float): [0,1] percentage of matched skills
        experience_match (list[dict]): [{"skill": "python", "required": 4, "candidate": 3, "status": "match"}, ...]
        exp_weight (float): Weight to give experience in overall score (0-1)

    Returns:
        float: Weighted overall similarity [0,1]
    """
    if not experience_match:
        return skills_similarity

    total_skills = len(experience_match)
    matched_count = sum(1 for e in experience_match if e["status"] == "match")
    exp_ratio = matched_count / total_skills if total_skills else 0

    overall = (1 - exp_weight) * skills_similarity + exp_weight * exp_ratio
    return round(overall, 3)


# -------------------------
# 2. Skills Similarity & Missing Keywords
# -------------------------
def semantic_skill_analysis(jd_skills: List[str], resume_skills: List[str], threshold: float = 0.75) -> Tuple[float, List[str]]:
    """
    Semantic skill matching with embeddings.
    Combines skill similarity scoring and missing keyword detection.

    Args:
        jd_skills (list[str]): Required skills from JD
        resume_skills (list[str]): Extracted skills from resume
        threshold (float): Similarity threshold for match

    Returns:
        tuple:
            skills_similarity (float): % of JD skills matched
            missing_keywords (list[str]): JD skills not matched semantically
    """
    if not jd_skills:
        return 0.0, []

    try:
        jd_vectors = np.array([get_embedding(skill) for skill in jd_skills])
        resume_vectors = np.array([get_embedding(skill) for skill in resume_skills]) if resume_skills else np.empty((0, jd_vectors.shape[1]))

        matched = 0
        missing = []

        for i, jd_vec in enumerate(jd_vectors):
            if resume_vectors.size == 0:
                missing.append(jd_skills[i])
                continue

            sims = cosine_similarity([jd_vec], resume_vectors)[0]
            if np.max(sims) >= threshold:
                matched += 1
            else:
                missing.append(jd_skills[i])

        skills_similarity = matched / len(jd_skills)
        return round(skills_similarity, 3), missing

    except Exception as e:
        logger.error(f"[Skills Similarity] Failed: {e}")
        return 0.0, jd_skills


# -------------------------
# 3. Experience Parsing
# -------------------------
def parse_experience_string(exp_str: str) -> Dict:
    """
    Extract numeric years and skill from JD experience string.
    Supports "2+ years", "3-4 years", multi-word skills.
    """
    pattern = r"(\d+)(?:\s*-\s*(\d+))?\+?\s*years?\s+(?:of\s+)?(?:experience\s+)?in\s+([\w\s\+#]+)"
    match = re.search(pattern, exp_str.lower())
    if match:
        years = int(match.group(2)) if match.group(2) else int(match.group(1))
        skill = match.group(3).strip()
        return {"skill": skill, "years_required": years}
    return None


# -------------------------
# 4. Experience Matching
# -------------------------
def match_experience(jd_experience: List[str], resume_experience: Dict[str, List]) -> List[Dict]:
    """
    Compare JD experience requirements with candidate's experience.

    Args:
        jd_experience (list[str]): ["4 years experience in java", ...]
        resume_experience (dict): {"CompanyA": ["java", "2018", "2022", "4"], ...}

    Returns:
        list[dict]: [{"skill": "java", "required": 4, "candidate": 4, "status": "match"}, ...]
    """
    matches = []

    for jd_exp in jd_experience:
        parsed = parse_experience_string(jd_exp)
        if not parsed:
            continue

        skill = parsed["skill"].lower()
        required_years = parsed["years_required"]

        candidate_years = 0
        for _, v in resume_experience.items():
            if len(v) < 4:
                continue
            res_skill = str(v[0]).lower()
            try:
                exp_years = int(v[3])
            except Exception:
                exp_years = 0
            if res_skill == skill:
                candidate_years += exp_years

        status = "match" if candidate_years >= required_years else "insufficient"
        matches.append({
            "skill": skill,
            "required": required_years,
            "candidate": candidate_years,
            "status": status
        })

    return matches


# -------------------------
# 5. Parse JD Experience to dict
# -------------------------
def parse_jd_experience(jd_experience: List[str]) -> Dict[str, int]:
    """
    Convert JD experience list to structured dict: {skill: required_years}
    """
    result = {}
    for exp in jd_experience:
        parsed = parse_experience_string(exp)
        if parsed:
            result[parsed["skill"].lower()] = parsed["years_required"]
    return result


# -------------------------
# 6. Aggregate Resume Experience
# -------------------------
def aggregate_resume_experience(resume_experience: Dict[str, List]) -> Dict[str, int]:
    """
    Aggregate candidate experience across all companies: {skill: total_years}
    """
    result = {}
    for _, v in resume_experience.items():
        if len(v) < 4:
            continue
        skill = str(v[0]).lower()
        try:
            years = int(v[3])
        except Exception:
            years = 0
        result[skill] = result.get(skill, 0) + years
    return result


# -------------------------
# 7. Normalize skill string
# -------------------------
def normalize_skill(skill: str) -> str:
    """
    Convert skill to lower case and strip whitespace.
    """
    if not skill:
        return ""
    return skill.strip().lower()
