"""
Similarity utilities for Phase 2 (Industry-level)
- Cosine similarity (overall JD ↔ Resume)
- Skills similarity (FAISS-based)
- Missing keyword detection
- Experience parsing & matching
"""

import re
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.embeddings.embedding_model import get_embedding
from app.embeddings.faiss_index import FaissIndex


# -------------------------
# 1. Overall Similarity
# -------------------------
def compute_overall_similarity(jd_vector: np.ndarray, resume_vector: np.ndarray) -> float:
    """
    Compute cosine similarity between JD and Resume embeddings.

    Args:
        jd_vector (np.ndarray): JD embedding
        resume_vector (np.ndarray): Resume embedding

    Returns:
        float: similarity score [0, 1]
    """
    sim = cosine_similarity([jd_vector], [resume_vector])[0][0]
    return float(sim)


# -------------------------
# 2. Skills Similarity (FAISS)
# -------------------------
def compute_skills_similarity(jd_skills: list, resume_skills: list) -> float:
    """
    Compute average similarity between JD skills and Resume skills using FAISS.
    Args:
        jd_skills (list[str]): Skills from JD
        resume_skills (list[str]): Skills from Resume
    Returns:
        float: average similarity score [0, 1]
    """
    if not jd_skills or not resume_skills:
        return 0.0

    # Generate embeddings
    jd_embeddings = [get_embedding(skill) for skill in jd_skills]
    resume_embeddings = [get_embedding(skill) for skill in resume_skills]

    # Create FAISS index for Resume skills
    dim = resume_embeddings[0].shape[0]
    faiss_index = FaissIndex(dim)
    ids = list(range(len(resume_embeddings)))
    faiss_index.add_vectors(resume_embeddings, ids)

    # Query each JD skill embedding → take max similarity
    sim_scores = []
    for jd_vec in jd_embeddings:
        results = faiss_index.search(jd_vec, top_k=1)
        if results:
            sim_scores.append(results[0][1])  # take top match score

    return float(np.mean(sim_scores))


# -------------------------
# 3. Missing Keywords
# -------------------------
def find_missing_keywords(jd_skills: list, resume_skills: list) -> list:
    """
    Identify skills from JD that are missing in Resume.

    Args:
        jd_skills (list[str]): JD skills
        resume_skills (list[str]): Resume skills

    Returns:
        list[str]: missing skills
    """
    jd_set = {s.lower() for s in jd_skills}
    resume_set = {s.lower() for s in resume_skills}
    missing = jd_set - resume_set
    return list(missing)


# -------------------------
# 4. Experience Parsing
# -------------------------
def parse_experience_string(exp_str: str):
    """
    Extract numeric years and skill from JD experience string.
    Example: "4 years experience in Java" -> {"skill": "java", "years_required": 4}
    """
    pattern = r"(\d+)\s*years.*in\s*(\w+)"
    match = re.search(pattern, exp_str.lower())
    if match:
        years = int(match.group(1))
        skill = match.group(2)
        return {"skill": skill, "years_required": years}
    return None


# def match_experience(jd_experience: list, resume_experience: dict):
#     """
#     Compare JD experience requirements with Resume experience.

#     Args:
#         jd_experience (list[str]): ["4 years experience in java", ...]
#         resume_experience (dict): {"Company": ["Role", start, end, years"]}

#     Returns:
#         list[dict]: [{"skill": ..., "required": ..., "candidate": ..., "status": "match/gap"}]
#     """
#     result = []

#     # Flatten Resume experience → skill: years
#     resume_skill_years = {}
#     for company, vals in resume_experience.items():
#         role, start, end, years_str = vals
#         # convert "3 years" or "3" to int
#         try:
#             years = int(re.search(r"\d+", str(years_str)).group(0))
#         except:
#             years = 0
#         resume_skill_years[role.lower()] = years

#     # Compare JD experience requirements with Resume
#     for exp_str in jd_experience:
#         parsed = parse_experience_string(exp_str)
#         if parsed:
#             skill = parsed["skill"]
#             required = parsed["years_required"]
#             candidate = resume_skill_years.get(skill, 0)
#             status = "match" if candidate >= required else "gap"
#             result.append({
#                 "skill": skill,
#                 "required": required,
#                 "candidate": candidate,
#                 "status": status
#             })

#     return result
# # -------------------------
# # 4. Experience Matching
# -------------------------
def match_experience(jd_experience: list, resume_experience: dict) -> list:
    """
    Compare JD experience requirements with candidate's experience.
    
    Args:
        jd_experience (list[str]): ["4 years experience in java", ...]
        resume_experience (dict): {"CompanyA": ["java", "2018", "2022", "4"], ...}
    
    Returns:
        list[dict]: [{"skill": "java", "required": 4, "candidate": 4, "status": "match"}, ...]
    """
    import re

    matches = []
    
    # Parse JD experience: extract years and skill
    for jd_exp in jd_experience:
        match = re.search(r'(\d+)\s*years.*in\s*(\w+)', jd_exp, re.IGNORECASE)
        if match:
            required_years = int(match.group(1))
            skill = match.group(2).lower()
            
            # Find candidate experience for the skill
            candidate_years = 0
            for _, v in resume_experience.items():
                res_skill = v[0].lower()
                exp_years = int(v[3]) if v[3].isdigit() else 0
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