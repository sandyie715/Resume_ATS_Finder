import requests
import json

# Replace with your local API URL
API_URL = "http://127.0.0.1:8000/similarity"

# -------------------------
# Simple Test Cases
# -------------------------
simple_test_cases = [
    {
        # Test Case 1: The Perfect Match
        # Goal: A basic sanity check. The resume should be a 100% match for the JD's skills and experience.
        "jd": {
            "skills": ["Python", "SQL"],
            "experience": ["2+ years of Python experience"]
        },
        "resume": {
            "Skills": ["Python", "SQL", "Git"],
            "Experience": {
                "Software Developer": ["Tech Solutions", "2022-01", "2024-01", "2"]
            }
        }
    },
    {
        # Test Case 2: The Simple Skill Mismatch
        # Goal: Check if the system can correctly identify a single missing skill.
        "jd": {
            "skills": ["Java", "Spring", "Maven"]
        },
        "resume": {
            "Skills": ["Java", "Maven"],
            "Experience": {
                "Java Developer": ["Code Corp", "2021-01", "2025-01", "4"]
            }
        }
    },
    {
        # Test Case 3: The Simple Experience Mismatch (Underqualified)
        # Goal: A direct test of the experience logic. The candidate has the skill but not enough years.
        "jd": {
            "skills": ["Python"],
            "experience": ["3+ years of Python experience"]
        },
        "resume": {
            "Skills": ["Python"],
            "Experience": {
                "Junior Developer": ["Startup Inc.", "2023-01", "2025-01", "2"]
            }
        }
    },
    {
        # Test Case 4: The Overqualified Candidate
        # Goal: Check if the system correctly handles a candidate who exceeds the experience requirement.
        "jd": {
            "skills": ["Java"],
            "experience": ["2+ years of Java experience"]
        },
        "resume": {
            "Skills": ["Java"],
            "Experience": {
                "Senior Java Engineer": ["Enterprise Software", "2020-01", "2025-01", "5"]
            }
        }
    },
    {
        # Test Case 5: The "No Relevant Experience" Candidate
        # Goal: The candidate lists the skill but has zero professional experience using it.
        "jd": {
            "skills": ["React"],
            "experience": ["2+ years of experience with React"]
        },
        "resume": {
            "Skills": ["React", "JavaScript", "HTML"],
            "Experience": {
                "Sales Associate": ["Retail World", "2022-01", "2025-01", "3"]
            }
        }
    }
]

# -------------------------
# Run Tests
# -------------------------
for idx, test_case in enumerate(simple_test_cases, start=1):
    print(f"\n--- Running Simple Test Case {idx} ---")
    try:
        response = requests.post(API_URL, json=test_case)
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=4))
        else:
            print(f"FAILED with status code {response.status_code}")
            print("Response:", response.text)
    except requests.exceptions.ConnectionError as e:
        print(f"FAILED: Could not connect to the API at {API_URL}.")
        print("Please ensure your FastAPI server is running.")
        break