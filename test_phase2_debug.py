# test_phase2_debug.py
import logging
from app.embeddings.pipeline import run_similarity_pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_phase2")

# ------------------------
# Example JD inputs (simulate both test cases)
# ------------------------
test_cases = [
    {
        "name": "Test Case 1",
        "jd": {
            "skills": ["Python", "AWS", "Django"],
            "experience": ["4 years experience in Python", "2 years experience in AWS"]
        },
        "resume": {
            "Skills": ["Python", "Django", "Flask"],
            "Experience": {
                "CompanyA": ["Python", "2018", "2022", "4"],
                "CompanyB": ["AWS", "2019", "2021", "2"]
            }
        }
    },
    {
        "name": "Test Case 2",
        "jd": {
            "skills": ["Java", "Spring", "Microservices"],
            "experience": ["3 years experience in Java", "2 years experience in Spring"]
        },
        "resume": {
            "Skills": ["Java", "Spring Boot", "Kafka"],
            "Experience": {
                "CompanyX": ["Java", "2017", "2020", "3"],
                "CompanyY": ["Spring", "2018", "2020", "2"]
            }
        }
    }
]

# ------------------------
# Run test cases
# ------------------------
for case in test_cases:
    print(f"\n--- {case['name']} ---")
    try:
        result = run_similarity_pipeline(case["jd"], case["resume"])
        print("Pipeline Result:")
        print(result)
    except Exception as e:
        logger.error(f"Exception for {case['name']}: {e}", exc_info=True)
        print(f"{case['name']} Failed with exception: {e}")
