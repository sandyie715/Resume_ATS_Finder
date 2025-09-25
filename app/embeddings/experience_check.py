"""
Experience Matching Utilities for Phase 2 (Robust Version)
- Parses JD experience requirements flexibly
- Aggregates candidate experience from resume
- Compares required vs actual years
- Normalizes skill names consistently
- Logs unknown skills for review
"""

import re
import logging
from typing import Dict, List, Any

# -------------------------
# Logger Setup
# -------------------------
logger = logging.getLogger("experience_check")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.FileHandler("logs/experience_check.log")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# -------------------------
# Skill Normalization
# -------------------------
SKILL_ALIASES = {
    "js": "javascript",
    "javascript framework": "javascript",
    "node.js": "nodejs",
    "node": "nodejs",
    "django framework": "django",
    "aws": "aws",
    "amazon web services": "aws",
    "gcp": "gcp",
    "google cloud platform": "gcp",
}

def normalize_skill(skill: str) -> str:
    if not skill or not isinstance(skill, str):
        return ""
    skill_clean = skill.lower().strip()
    normalized = SKILL_ALIASES.get(skill_clean, skill_clean)
    if normalized == skill_clean:
        logger.info(f"Unknown skill detected: '{skill_clean}'")
    return normalized

# -------------------------
# 1. Parse JD Experience
# -------------------------
def parse_jd_experience(jd_experience_list: List[str]) -> Dict[str, int]:
    """
    Convert JD experience strings into structured dictionary.
    Supports patterns like:
        "4 years experience in Python"
        "2+ yrs in AWS"
        "1-2 years with Django"
    Returns:
        {"python": 4, "aws": 2}
    """
    exp_dict = {}
    for exp in jd_experience_list:
        if not isinstance(exp, str):
            continue
        match = re.search(r'(\d+)(?:-(\d+)|\+)?\s*years?.*?(?:in|with|on)\s+([\w\s\.\+#]+)', exp, re.IGNORECASE)
        if match:
            min_years = int(match.group(1))
            max_years = int(match.group(2)) if match.group(2) else min_years
            skill = normalize_skill(match.group(3))
            exp_dict[skill] = max_years  # use the upper bound for required experience
        else:
            logger.warning(f"[JD Parsing] Could not parse experience string: '{exp}'")
    return exp_dict

# -------------------------
# 2. Aggregate Resume Experience
# -------------------------
def aggregate_resume_experience(resume_experience: Dict[str, Any]) -> Dict[str, int]:
    """
    Aggregate total experience per skill from the candidate's resume.
    Handles:
        - Experience entries as list: [skill, start, end, duration]
        - Experience entries as string
    Returns:
        {"python": 4, "aws": 2}
    """
    skill_years = {}
    for _, details in resume_experience.items():
        try:
            if isinstance(details, str):
                skill = normalize_skill(details)
                skill_years[skill] = skill_years.get(skill, 0) + 0
            elif isinstance(details, list) and len(details) >= 4:
                skill = normalize_skill(details[0])
                try:
                    years = int(details[3])
                except (ValueError, TypeError):
                    years = 0
                skill_years[skill] = skill_years.get(skill, 0) + years
            else:
                logger.warning(f"[Resume Exp] Skipped invalid experience entry: {details}")
        except Exception as e:
            logger.error(f"[Resume Exp] Error processing details {details}: {e}")
    return skill_years

# -------------------------
# 3. Compare Experience
# -------------------------
def check_duration(jd_exp: Dict[str, int], resume_exp: Dict[str, int]) -> List[Dict]:
    """
    Compare required vs actual experience for each skill.
    Returns:
        [
            {"skill": "python", "required": 4, "candidate": 3, "status": "insufficient"},
            {"skill": "aws", "required": 2, "candidate": 2, "status": "match"}
        ]
    """
    results = []
    for skill, required in jd_exp.items():
        candidate_years = resume_exp.get(skill, 0)
        status = "match" if candidate_years >= required else "insufficient"
        results.append({
            "skill": skill,
            "required": required,
            "candidate": candidate_years,
            "status": status
        })
    return results