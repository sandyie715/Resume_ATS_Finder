"""
Pydantic schemas for Phase 2 similarity API
"""

from pydantic import BaseModel
from typing import List


class JDInput(BaseModel):
    skills: List[str]
    experience: List[str] = []


class ResumeInput(BaseModel):
    Skills: List[str]
    Experience: dict = {}  # company → [role, start, end, duration]


class SimilarityResponse(BaseModel):
    overall_similarity: float
    skills_similarity: float
    missing_keywords: List[str]