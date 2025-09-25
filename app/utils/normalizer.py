"""
Normalizer Utilities for Phase 2
--------------------------------
Transforms raw parsed JD & Resume data into a clean, standardized format
for the similarity pipeline.

Responsibilities:
- Normalize skill names and handle common synonyms / typos
- Extract numeric experience from messy strings
- Merge scattered experience entries per skill
- Validate structure and log anomalies robustly
"""

import re
import logging
from typing import Dict, Any, List, Tuple

# -------------------------
# Logger Setup
# -------------------------
logger = logging.getLogger("normalizer")
logger.setLevel(logging.INFO)

# Avoid duplicate handlers during reloads
if not logger.handlers:
    handler = logging.FileHandler("logs/normalizer.log")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# -------------------------
# Skill Synonyms Dictionary
# -------------------------
SKILL_SYNONYMS = {
    # JavaScript variants
    "js": "javascript",
    "javascript framework": "javascript",
    "javascript": "javascript",
    "reactjs": "react",
    "react": "react",
    "node": "nodejs",
    "nodejs": "nodejs",
    "node.js": "nodejs",

    # Python
    "py": "python",
    "python": "python",

    # Django
    "django framework": "django",
    "django": "django",

    # C/C++
    "c++": "c++",
    "cpp": "c++",
    "c#": "c#",

    # Cloud & DevOps
    "aws": "aws",
    "amazon web services": "aws",
    "gcp": "gcp",
    "google cloud platform": "gcp",
    "docker": "docker",
    "kubernetes": "kubernetes",

    # ML/AI
    "tensorflow": "tensorflow",
    "pytorch": "pytorch",
    "huggingface transformers": "huggingface transformers",
    "mlflow": "mlflow",
    "scikit-learn": "scikit-learn",
}

def normalize_skill_name(skill: str) -> str:
    """
    Normalize skill names:
    - Lowercase, strip spaces, remove punctuation
    - Map synonyms from SKILL_SYNONYMS
    - Fallback partial matching
    - Log unknown skills for future dictionary updates
    """
    if not skill or not isinstance(skill, str):
        return ""

    # Clean skill string
    skill_clean = skill.strip().lower()
    skill_clean = re.sub(r"[^a-z0-9\s\+\#]", "", skill_clean)  # remove punctuation

    # Direct mapping
    if skill_clean in SKILL_SYNONYMS:
        return SKILL_SYNONYMS[skill_clean]

    # Partial match mapping
    for key, val in SKILL_SYNONYMS.items():
        if key in skill_clean:
            return val

    # Log unknown skill for review
    logger.info(f"Unknown skill detected: '{skill_clean}'")

    return skill_clean

# -------------------------
# JD Experience Parsing
# -------------------------
def parse_experience_string(exp_str: str) -> Tuple[int, str]:
    """
    Parse JD experience string like:
        "4 years experience in Python"
        "2+ yrs of AWS"
    → (4, 'python')
    """
    if not exp_str or not isinstance(exp_str, str):
        return 0, ""

    try:
        match = re.search(r'(\d+)\s*[\+]*\s*years?.*?(?:in|with|on)?\s*([\w\s\.\#]+)', exp_str, re.IGNORECASE)
        if match:
            years = int(match.group(1))
            skill = normalize_skill_name(match.group(2))
            return years, skill
        else:
            logger.warning(f"[JD Parsing] Could not parse experience string: '{exp_str}'")
            return 0, ""
    except Exception as e:
        logger.error(f"[JD Parsing] Exception parsing experience string '{exp_str}': {e}")
        return 0, ""

# -------------------------
# JD Normalization
# -------------------------
def normalize_jd(raw_jd: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize JD data into Phase 2-ready format."""
    if not isinstance(raw_jd, dict):
        logger.error("[JD] Invalid JD input format.")
        return {"skills": [], "experience": []}

    normalized_skills: List[str] = []
    normalized_exp: List[str] = []

    # Normalize skills
    for skill in raw_jd.get("skills", []):
        norm_skill = normalize_skill_name(skill)
        if norm_skill:
            normalized_skills.append(norm_skill)
        else:
            logger.warning(f"[JD Skill] Empty or invalid JD skill: {skill}")

    # Normalize experience strings
    for exp in raw_jd.get("experience", []):
        years, skill = parse_experience_string(exp)
        if years > 0 and skill:
            normalized_exp.append(f"{years} years experience in {skill}")

    return {
        "skills": sorted(set(normalized_skills)),
        "experience": normalized_exp
    }

# -------------------------
# Resume Normalization
# -------------------------
def normalize_resume(raw_resume: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize Resume data into Phase 2-ready format."""
    if not isinstance(raw_resume, dict):
        logger.error("[Resume] Invalid resume input format.")
        return {"Skills": [], "Experience": {}}

    normalized_skills: List[str] = []
    normalized_experience: Dict[str, List[Any]] = {}

    # Normalize skills
    skills_raw = raw_resume.get("Skills", [])
    if isinstance(skills_raw, str):
        skills_raw = [s.strip() for s in skills_raw.split(",") if s.strip()]

    for skill in skills_raw:
        norm_skill = normalize_skill_name(skill)
        if norm_skill:
            normalized_skills.append(norm_skill)

    # Normalize and merge experience
    for company, details in raw_resume.get("Experience", {}).items():
        if isinstance(details, str):
            details = [details]
        details = details[:4] + [""] * (4 - len(details))

        skill = normalize_skill_name(details[0])

        # Parse start, end, duration
        try:
            start = int(re.search(r'\d{4}', str(details[1])).group()) if details[1] else 0
        except:
            start = 0
        try:
            end = int(re.search(r'\d{4}', str(details[2])).group()) if details[2] else 0
        except:
            end = 0
        try:
            duration = int(re.search(r'\d+', str(details[3])).group()) if details[3] else 0
        except:
            duration = 0

        if skill in normalized_experience:
            normalized_experience[skill][3] += duration
        else:
            normalized_experience[skill] = [skill, start, end, duration]

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
