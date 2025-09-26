# utils/similarity.py
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json

# Load transformer model (MiniLM)
model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_texts(texts):
    """Convert list of texts into embeddings"""
    return model.encode(texts, convert_to_numpy=True)

def compute_similarity(text_a, text_b):
    """Cosine similarity between two texts"""
    emb_a = embed_texts([text_a])[0]
    emb_b = embed_texts([text_b])[0]
    return float(np.dot(emb_a, emb_b) / (np.linalg.norm(emb_a) * np.linalg.norm(emb_b)))

def jd_resume_similarity(combined_json_path="combined_output.json"):
    """
    Compute overall similarity between JD and Resume
    + skill-to-skill matching to detect missing keywords
    """
    with open(combined_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    resume = data.get("resume", {})
    jd = data.get("jd", {})

    resume_text = " ".join(resume.get("Skills", [])) + " " + str(resume)
    jd_text = " ".join(jd.get("skills", [])) + " " + str(jd)

    # Overall JD vs Resume similarity
    overall_score = compute_similarity(jd_text, resume_text)

    # Skill matching
    resume_skills = set([s.lower() for s in resume.get("Skills", [])])
    jd_skills = set([s.lower() for s in jd.get("skills", [])])

    missing_skills = list(jd_skills - resume_skills)
    skill_overlap = list(jd_skills & resume_skills)

    return {
        "overall_similarity": round(overall_score, 3),
        "matched_skills": skill_overlap,
        "missing_skills": missing_skills
    }
