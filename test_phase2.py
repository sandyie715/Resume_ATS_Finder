import requests
import json

# Replace with your local API URL
API_URL = "http://127.0.0.1:8000/similarity"

# -------------------------
# Test Cases
# -------------------------
test_cases = [
    {
        "jd": {
            "skills": ["Python", "Java", "SQL"],
            "experience": ["3 years experience in Python", "2 years experience in Java"]
        },
        "resume": {
            "Skills": ["Python", "Java", "SQL"],
            "Experience": {
                "CompanyA": ["Python", "2018", "2021", "3"],
                "CompanyB": ["Java", "2019", "2021", "2"]
            }
        }
    },
    {
        "jd": {
            "skills": ["Python", "Java", "React"],
            "experience": ["2 years experience in Python", "1 years experience in React"]
        },
        "resume": {
            "Skills": ["Python", "Java"],
            "Experience": {
                "CompanyA": ["Python", "2019", "2021", "2"],
                "CompanyB": ["Java", "2020", "2021", "1"]
            }
        }
    },
    {
        "jd": {
            "skills": ["JavaScript", "Django", "SQL"],
            "experience": ["3 years experience in JavaScript", "2 years experience in Django"]
        },
        "resume": {
            "Skills": ["JS", "Django Framework", "SQL"],
            "Experience": {
                "CompanyA": ["JS", "2017", "2020", "3"],
                "CompanyB": ["Django Framework", "2018", "2020", "2"]
            }
        }
    },
    {
        "jd": {
            "skills": ["Python", "AWS", "Docker"],
            "experience": ["4 years experience in Python", "2 years experience in AWS"]
        },
        "resume": {
            "Skills": ["Python", "AWS", "Docker"],
            "Experience": {
                "CompanyA": ["Python", "2018", "2021", "3"],
                "CompanyB": ["AWS", "2021", "2022", "1"]
            }
        }
    },
    {
        "jd": {
            "skills": ["Java", "SQL"],
            "experience": ["2 years experience in Java"]
        },
        "resume": {
            "Skills": ["Java", "SQL", "Python", "React"],
            "Experience": {
                "CompanyA": ["Java", "2018", "2020", "2"],
                "CompanyB": ["Python", "2019", "2022", "3"]
            }
        }
    }
]

# -------------------------
# Run Tests
# -------------------------
for idx, test_case in enumerate(test_cases, start=1):
    response = requests.post(API_URL, json=test_case)
    if response.status_code == 200:
        print(f"\n--- Test Case {idx} ---")
        print(json.dumps(response.json(), indent=4))
    else:
        print(f"Test Case {idx} failed with status code {response.status_code}")
