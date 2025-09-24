"""
FastAPI router for Phase 2: Embeddings & Similarity Matching
"""

from fastapi import APIRouter, HTTPException
from app.embeddings.pipeline import run_similarity_pipeline
from app.schemas.similarity_schema import JDInput, ResumeInput, SimilarityResponse

router = APIRouter(prefix="/similarity", tags=["Similarity Matching"])


@router.post("/", response_model=SimilarityResponse)
def similarity_endpoint(jd: JDInput, resume: ResumeInput):
    """
    Endpoint for JD ↔ Resume similarity matching.

    Args:
        jd (JDInput): Parsed JD JSON
        resume (ResumeInput): Parsed Resume JSON

    Returns:
        SimilarityResponse: JSON with similarity scores & missing keywords
    """
    try:
        result = run_similarity_pipeline(jd.dict(), resume.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))