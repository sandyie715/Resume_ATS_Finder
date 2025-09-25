import pytest
from app.utils.normalizer import normalize_parsed_data, normalize_skill_name

def test_unknown_skill_logged_and_preserved(caplog):
    """
    Test that unknown skills are:
    1. Preserved in the normalized output
    2. Logged for review
    """
    raw_jd = {
        "skills": ["Elixir", "RustLang"],  # unknown skills
        "experience": ["3 years experience in Elixir"]
    }
    raw_resume = {
        "Skills": ["Kotlin", "Scala"],  # unknown skills
        "Experience": {
            "CompanyX": ["Elixir", "2019", "2022", "3"],
            "CompanyY": ["Scala", "2018", "2021", "3"]
        }
    }

    with caplog.at_level("INFO"):
        jd_cleaned, resume_cleaned = normalize_parsed_data(raw_jd, raw_resume)

        # Check JD skills preserved
        assert "elixir" in jd_cleaned["skills"]
        assert "rustlang" in jd_cleaned["skills"]

        # Check Resume skills preserved
        assert "kotlin" in resume_cleaned["Skills"]
        assert "scala" in resume_cleaned["Skills"]

        # Check logging for unknown skills
        assert any("unknown skill" in message.lower() for message in caplog.text.splitlines())
