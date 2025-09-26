"""
Normalizer Utilities for Phase 2
--------------------------------
Helper functions for robust skill and experience normalization.
Includes:
- Skill splitting
- Date range parsing
- Duration calculation
- Logging of anomalies
- Skill normalization
"""

import re
import logging
from typing import List, Optional, Tuple
from dateutil import parser
from datetime import datetime

# -------------------------
# Logger Setup
# -------------------------
logger = logging.getLogger("normalizer_utils")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.FileHandler("logs/normalizer_utils.log")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# -------------------------
# Skill Synonyms Dictionary (from normalizer.py)
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

# -------------------------
# Skill Normalization
# -------------------------
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
# Skill splitting
# -------------------------
def split_skill_string(raw_skill: str) -> List[str]:
    """
    Split a raw skill string into canonical list.
    Handles: comma, semicolon, pipe, 'and', sentence patterns like 'Skilled in X and Y'.
    Returns normalized, lowercased skills.
    """
    if not raw_skill or not isinstance(raw_skill, str):
        return []

    try:
        clean = re.sub(r'\(.*?\)', '', raw_skill).strip()
        parts = re.split(r'[;,|]', clean)
        skills = []
        for part in parts:
            sub_parts = re.split(r'\band\b', part, flags=re.I)
            for s in sub_parts:
                skill = normalize_skill_name(s.strip())
                if skill:
                    skills.append(skill)
        return skills
    except Exception as e:
        logger.error(f"[Skill Split] Failed to split '{raw_skill}': {e}")
        return []

# -------------------------
# Date parsing
# -------------------------
def parse_date_or_none(date_str: str) -> Optional[datetime]:
    if not date_str or not isinstance(date_str, str):
        return None
    try:
        return parser.parse(date_str)
    except Exception:
        logger.warning(f"[Date Parse] Could not parse date: '{date_str}'")
        return None

# -------------------------
# Duration calculation
# -------------------------
def compute_duration_in_years(start: Optional[datetime], end: Optional[datetime]) -> float:
    try:
        if not start:
            return 0.0
        if not end:
            end = datetime.now()
        delta = end - start
        years = delta.days / 365.25
        return round(years, 2)
    except Exception as e:
        logger.error(f"[Duration Calc] Failed for start={start}, end={end}: {e}")
        return 0.0

# -------------------------
# Experience string parsing (JD)
# -------------------------
def parse_experience_string(exp_str: str) -> Tuple[float, List[str]]:
    if not exp_str or not isinstance(exp_str, str):
        return 0.0, []

    try:
        match = re.search(r'(\d+)(?:\s*-\s*(\d+))?\+?\s*(?:yrs?|years?)', exp_str, re.IGNORECASE)
        if match:
            start_years = int(match.group(1))
            end_years = int(match.group(2)) if match.group(2) else start_years
            duration = float(end_years)
        else:
            duration = 0.0

        skill_match = re.search(r'(?:in|of|with)?\s*([\w\s\+\#&]+)', exp_str, re.IGNORECASE)
        skill_str = skill_match.group(1).strip() if skill_match else ""
        skills = split_skill_string(skill_str)
        return duration, skills
    except Exception as e:
        logger.error(f"[JD Exp Parse] Failed to parse '{exp_str}': {e}")
        return 0.0, []

# -------------------------
# Misc helpers
# -------------------------
def sanitize_string(s: str) -> str:
    if not s or not isinstance(s, str):
        return ""
    try:
        s_clean = s.strip().lower()
        s_clean = re.sub(r"[^a-z0-9\s\+\#]", "", s_clean)
        return s_clean
    except Exception as e:
        logger.error(f"[Sanitize String] Failed for '{s}': {e}")
        return ""