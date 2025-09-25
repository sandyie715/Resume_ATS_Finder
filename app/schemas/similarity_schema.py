from pydantic import BaseModel
from typing import List, Dict, Union, Any

# -------------------------
# Input Schemas
# -------------------------
class JDInput(BaseModel):
    skills: List[str]
    experience: List[str] = []  # Optional, defaults to empty list

class ResumeInput(BaseModel):
    # Skills can be a list of strings or a single comma-separated string
    Skills: Union[List[str], str] = []

    # Experience can be a dict (company → list of details) or string
    Experience: Union[Dict[str, Union[List[Any], str]], str] = {}

# -------------------------
# Output Schemas
# -------------------------
class ExperienceMatch(BaseModel):
    skill: str
    required: int
    candidate: int
    status: str  # "match" or "insufficient"

class SimilarityResponse(BaseModel):
    overall_similarity: float
    skills_similarity: float
    experience_similarity: float  # Added to track experience separately
    missing_keywords: List[str]
    experience_match: List[ExperienceMatch]
