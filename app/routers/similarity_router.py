"""
FastAPI router for Phase 2: Embeddings & Similarity Matching (Step 5+ Robust)
"""

from fastapi import APIRouter
from app.embeddings.pipeline import run_similarity_pipeline
from app.schemas.similarity_schema import JDInput, ResumeInput, SimilarityResponse
from typing import Dict, Any
import logging
import re
import traceback

router = APIRouter(prefix="/similarity", tags=["Similarity Matching"])
logger = logging.getLogger("similarity_router")
logging.basicConfig(level=logging.INFO)


# -----------------------------
# Helper functions
# -----------------------------
def normalize_resume_input(resume: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize resume fields safely.
    Converts Skills to list, Experience to dict of lists, and parses durations to integers.
    """
    normalized = resume.copy()

    # ---------------------
    # Skills
    # ---------------------
    skills = normalized.get("Skills", [])
    if isinstance(skills, str):
        normalized["Skills"] = [s.strip() for s in skills.split(",") if s.strip()]
    elif isinstance(skills, list):
        normalized["Skills"] = [str(s).strip() for s in skills if s]
    else:
        normalized["Skills"] = []

    # ---------------------
    # Experience
    # ---------------------
    experience = normalized.get("Experience", {})
    normalized_exp = {}
    if isinstance(experience, dict):
        for k, v in experience.items():
            if isinstance(v, str):
                normalized_exp[k] = [s.strip() for s in v.split(",") if s.strip()]
            elif isinstance(v, list):
                normalized_exp[k] = [str(x).strip() for x in v]
            else:
                normalized_exp[k] = [str(v)]
    normalized["Experience"] = normalized_exp

    # ---------------------
    # Parse durations
    # ---------------------
    for exp_key, exp_values in normalized["Experience"].items():
        for i, val in enumerate(exp_values):
            try:
                if isinstance(val, str):
                    matches = re.findall(r"\d+", val)
                    exp_values[i] = max(int(x) for x in matches) if matches else 0
                elif isinstance(val, (int, float)):
                    exp_values[i] = int(val)
                else:
                    exp_values[i] = 0
            except Exception as e:
                logger.warning(f"[Resume Exp] Could not parse '{val}' for {exp_key}: {e}")
                exp_values[i] = 0

    return normalized


# -----------------------------
# Endpoint
# -----------------------------
@router.post("/", response_model=SimilarityResponse)
def similarity_endpoint(jd: JDInput, resume: ResumeInput):
    """
    JD ↔ Resume similarity endpoint.
    Returns structured similarity, missing keywords, and experience matches.
    Fully defensive to avoid 500 errors.
    """
    try:
        # Normalize resume input
        resume_data = normalize_resume_input(resume.dict() if resume else {})

        # Defensive logging
        logger.info(f"Received JD: {jd.dict() if jd else {}}")
        logger.info(f"Normalized Resume: {resume_data}")

        # Run pipeline safely
        pipeline_result = run_similarity_pipeline(jd.dict() if jd else {}, resume_data)

        # -----------------------------
        # Ensure experience_match is a list
        # -----------------------------
        experience_match = pipeline_result.get("experience_match", [])
        if not isinstance(experience_match, list):
            experience_match = []

        # Validate each experience entry
        for item in experience_match:
            try:
                item["skill"] = str(item.get("skill", ""))
                item["required"] = int(item.get("required", 0))
                item["candidate"] = int(item.get("candidate", 0))
                item["status"] = str(item.get("status", "insufficient"))
            except Exception as e:
                logger.warning(f"[Experience Match] Invalid entry {item}: {e}")
                item.update({"skill": "", "required": 0, "candidate": 0, "status": "insufficient"})

        pipeline_result["experience_match"] = experience_match

        # -----------------------------
        # Ensure missing_keywords is a list
        # -----------------------------
        if not isinstance(pipeline_result.get("missing_keywords", []), list):
            pipeline_result["missing_keywords"] = []

        # -----------------------------
        # Ensure experience_similarity is always a float
        # -----------------------------
        try:
            pipeline_result["experience_similarity"] = float(
                pipeline_result.get("experience_similarity", 0.0)
            )
        except Exception as e:
            logger.warning(f"[experience_similarity] Could not convert to float: {e}")
            pipeline_result["experience_similarity"] = 0.0

        # -----------------------------
        # Defensive: overall_similarity & skills_similarity
        # -----------------------------
        try:
            pipeline_result["overall_similarity"] = float(pipeline_result.get("overall_similarity", 0.0))
        except:
            pipeline_result["overall_similarity"] = 0.0

        try:
            pipeline_result["skills_similarity"] = float(pipeline_result.get("skills_similarity", 0.0))
        except:
            pipeline_result["skills_similarity"] = 0.0

        return pipeline_result

    except Exception as e:
        logger.error(f"[Similarity Router] Exception: {e}\n{traceback.format_exc()}")
        # Return safe fallback response instead of 500
        return {
            "overall_similarity": 0.0,
            "skills_similarity": 0.0,
            "experience_similarity": 0.0,
            "missing_keywords": [],
            "experience_match": []
        }
