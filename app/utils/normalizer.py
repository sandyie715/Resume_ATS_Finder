"""
Normalizer for Phase 2
----------------------
Transforms raw parsed JD & Resume data into a clean, standardized format
for the similarity pipeline.

Now includes optional LLM preprocessing to improve normalization quality.
"""

import re
import logging
from typing import Dict, Any, List, Tuple

# -------------------------
# Import helpers from normalizer_utils
# -------------------------
from app.utils.normalizer_utils import (
    split_skill_string,
    parse_date_or_none,
    compute_duration_in_years,
    normalize_skill_name,  # imported from utils to solve circular import
    parse_experience_string
)

# -------------------------
# Optional: Import LLM preprocessor
# -------------------------
try:
    from app.llm.llm_preprocessor import preprocess_with_llm
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

# -------------------------
# Logger Setup
# -------------------------
logger = logging.getLogger("normalizer")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.FileHandler("logs/normalizer.log")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


# -------------------------
# JD Normalization
# -------------------------
def normalize_jd(raw_jd: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize JD data into Phase 2-ready format with robust error handling."""

    # ✅ Step 1: Optional LLM Preprocessing
    if LLM_AVAILABLE:
        try:
            logger.info("[JD] Running LLM preprocessor on raw JD...")
            processed = preprocess_with_llm({"jd": raw_jd, "resume": {}})
            raw_jd = processed.get("jd", raw_jd)
            logger.info("[JD] LLM preprocessing completed successfully.")
        except Exception as e:
            logger.error(f"[JD] LLM preprocessing failed: {e}. Continuing with fallback logic.")

    if not isinstance(raw_jd, dict):
        logger.error("[JD] Invalid JD input format.")
        return {"skills": [], "experience": []}

    normalized_skills: List[str] = []
    normalized_exp: List[str] = []

    # ✅ Normalize skills
    for skill_entry in raw_jd.get("skills", []):
        for skill in split_skill_string(skill_entry):
            norm_skill = normalize_skill_name(skill)
            if norm_skill:
                normalized_skills.append(norm_skill)
            else:
                logger.warning(f"[JD Skill] Empty or invalid JD skill: {skill_entry}")

    # ✅ Normalize experience strings
    for exp in raw_jd.get("experience", []):
        try:
            years, skills = parse_experience_string(exp)
            for skill in skills:
                normalized_exp.append(f"{years} years experience in {skill}")
        except Exception as e:
            logger.error(f"[JD Exp] Error parsing experience string '{exp}': {e}")

    return {
        "skills": sorted(set(normalized_skills)),
        "experience": normalized_exp
    }


# -------------------------
# Resume Normalization
# -------------------------
def normalize_resume(raw_resume: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize Resume data into Phase 2-ready format with robust error handling."""

    # ✅ Step 1: Optional LLM Preprocessing
    if LLM_AVAILABLE:
        try:
            logger.info("[Resume] Running LLM preprocessor on raw resume...")
            processed = preprocess_with_llm({"resume": raw_resume, "jd": {}})
            raw_resume = processed.get("resume", raw_resume)
            logger.info("[Resume] LLM preprocessing completed successfully.")
        except Exception as e:
            logger.error(f"[Resume] LLM preprocessing failed: {e}. Continuing with fallback logic.")

    if not isinstance(raw_resume, dict):
        logger.error("[Resume] Invalid resume input format.")
        return {"Skills": [], "Experience": {}}

    normalized_skills: List[str] = []
    normalized_experience: Dict[str, List[Any]] = {}

    # ✅ Normalize skills
    skills_raw = raw_resume.get("Skills", [])
    if isinstance(skills_raw, str):
        skills_raw = split_skill_string(skills_raw)

    for skill in skills_raw:
        norm_skill = normalize_skill_name(skill)
        if norm_skill:
            normalized_skills.append(norm_skill)

    # ✅ Normalize and merge experience
    for company, details in raw_resume.get("Experience", {}).items():
        if isinstance(details, str):
            details = [details]
        details = details[:4] + [""] * (4 - len(details))  # pad missing fields

        # Support multiple skills in experience
        skills_in_entry = split_skill_string(details[0])
        if not skills_in_entry:
            skills_in_entry = ["unknown"]

        try:
            start_date = parse_date_or_none(details[1])
            end_date = parse_date_or_none(details[2])
            duration = compute_duration_in_years(start_date, end_date)
        except Exception as e:
            logger.error(f"[Resume Exp] Error parsing experience for {company}: {e}")
            start_date = end_date = None
            duration = 0.0

        # Merge experience per skill
        for raw_skill in skills_in_entry:
            skill = normalize_skill_name(raw_skill)
            if skill in normalized_experience:
                normalized_experience[skill][3] += duration
            else:
                normalized_experience[skill] = [skill, details[1], details[2], duration]

    return {
        "Skills": sorted(set(normalized_skills)),
        "Experience": normalized_experience
    }


# -------------------------
# Master Normalizer
# -------------------------
def normalize_parsed_data(raw_jd: Dict[str, Any], raw_resume: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Main entry point for preprocessing JD & Resume data.
    Returns:
        (normalized_jd, normalized_resume)
    """
    logger.info("Starting normalization of JD and Resume data...")
    try:
        jd_cleaned = normalize_jd(raw_jd)
        resume_cleaned = normalize_resume(raw_resume)
        logger.info("Normalization completed successfully.")
        return jd_cleaned, resume_cleaned
    except Exception as e:
        logger.critical(f"[Normalizer] Fatal error during normalization: {e}")
        raise ValueError("Normalization failed. Check logs for details.")
