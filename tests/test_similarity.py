import pytest
from app.embeddings.pipeline import run_similarity_pipeline
from app.embeddings.similarity import parse_experience_string, match_experience

# -------------------------
# Sample JD & Resume
# -------------------------
jd_sample = {
    "skills": ["python", "java", "docker"],
    "experience": ["4 years experience in java", "2 years python"]
}

resume_sample = {
    "Skills": ["python", "c++", "docker"],
    "Experience": {
        "CompanyA": ["java", "2018", "2022", "4"],
        "CompanyB": ["python", "2021", "2023", "2"]
    }
}

# -------------------------
# Test: Parse Experience String
# -------------------------
def test_parse_experience_string():
    parsed = parse_experience_string("4 years experience in java")
    assert parsed["skill"] == "java"
    assert parsed["years_required"] == 4

# -------------------------
# Test: Experience Matching
# -------------------------
def test_match_experience():
    exp_result = match_experience(jd_sample["experience"], resume_sample["Experience"])
    assert len(exp_result) == 2
    assert exp_result[0]["status"] == "match"
    assert exp_result[1]["status"] == "match"
    assert exp_result[0]["candidate"] == 4
    assert exp_result[1]["candidate"] == 2

# -------------------------
# Test: Full Pipeline
# -------------------------
def test_pipeline_output():
    output = run_similarity_pipeline(jd_sample, resume_sample)
    
    # Check keys in output
    assert "overall_similarity" in output
    assert "skills_similarity" in output
    assert "missing_keywords" in output
    assert "experience_match" in output

    # Check experience_match content
    exp_match = output["experience_match"]
    assert exp_match[0]["skill"] == "java"
    assert exp_match[0]["status"] == "match"
    assert exp_match[1]["skill"] == "python"
    assert exp_match[1]["status"] == "match"

    # Check missing keywords
    assert "java" not in output["missing_keywords"]  # matched
    assert "docker" not in output["missing_keywords"]  # matched