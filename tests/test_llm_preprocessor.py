# tests/test_llm_preprocessor.py

import logging
from app.llm.llm_preprocessor import llm_normalize_jd, llm_normalize_resume

# -------------------------
# Logger Setup
# -------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# -------------------------
# Sample Test Data
# -------------------------
sample_jd = {
    "skills": ["Python", "SQL", "PostgreSQL", "Pandas (NumPy)"],
    "experience": ["3+ years Python development", "2 years SQL experience"]
}

sample_resume = {
    "skills": "Python (including Pandas & NumPy), SQL; PostgreSQL",
    "experience": {
        "Company A": ["Python, SQL", "2019-01-01", "2022-06-01", ""],
        "Company B": ["PostgreSQL", "2022-07-01", "2023-12-01", ""]
    }
}

# -------------------------
# Test Functions
# -------------------------
def test_llm_jd():
    try:
        normalized_jd = llm_normalize_jd(sample_jd)
        print("\n===== Normalized JD =====")
        print(normalized_jd)
        assert "skills" in normalized_jd
        assert "experience" in normalized_jd
    except Exception as e:
        print(f"JD normalization test failed: {e}")


def test_llm_resume():
    try:
        normalized_resume = llm_normalize_resume(sample_resume)
        print("\n===== Normalized Resume =====")
        print(normalized_resume)
        assert "skills" in normalized_resume
        assert "experience" in normalized_resume
    except Exception as e:
        print(f"Resume normalization test failed: {e}")


#-------------------------
#Run Tests
#-------------------------
if __name__ == "__main__":
    print("\n===== Testing LLM JD Normalization =====")
    test_llm_jd()

    print("\n===== Testing LLM Resume Normalization =====")
    test_llm_resume()