from pydantic import BaseModel, Field
from typing import List, Dict, Union, Any, Optional

# -------------------------
# Input Schemas
# -------------------------
class JDInput(BaseModel):
    skills: Optional[List[str]] = Field(default_factory=list)
    experience: Optional[List[str]] = Field(default_factory=list)  # Optional, defaults to empty list

class ResumeInput(BaseModel):
    # Skills can be a list of strings or a single comma-separated string
    Skills: Optional[Union[List[str], str]] = Field(default_factory=list)

    # Experience can be a dict (company → list of details) or string
    Experience: Optional[Union[Dict[str, Union[List[Any], str]], str]] = Field(default_factory=dict)

# -------------------------
# Output Schemas
# -------------------------
class ExperienceMatch(BaseModel):
    skill: str
    required: float
    candidate: float
    status: str  # "match" or "insufficient"

class SimilarityResponse(BaseModel):
    overall_similarity: float = 0.0
    skills_similarity: float = 0.0
    experience_similarity: float = 0.0
    missing_keywords: List[str] = Field(default_factory=list)
    experience_match: List[ExperienceMatch] = Field(default_factory=list)
