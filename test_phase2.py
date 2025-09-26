import requests
import json

# Replace with your local API URL
API_URL = "http://127.0.0.1:8000/similarity"

# -------------------------
# Step 1: Normalization Test Cases
# -------------------------
normalization_test_cases = [
    {
        # Test Case 1: The "Mixed Delimiter" Skills List
        # Goal: Can the parser correctly extract skills from a single string with commas, semicolons, and pipes?
        "jd": {
            "skills": ["Python", "SQL", "Java", "Docker", "Kubernetes"]
        },
        "resume": {
            "Skills": "Python, SQL; Java | Docker, Kubernetes",
            "Experience": {}
        }
    },
    {
        # Test Case 2: The "Skills in a Sentence" Format
        # Goal: Can the parser extract skills from natural language sentences, ignoring filler words?
        "jd": {
            "skills": ["Java", "Python", "Spring Boot", "AWS"]
        },
        "resume": {
            "Skills": "Proficient in Java and Python. Also have experience with Spring Boot and some exposure to AWS.",
            "Experience": {}
        }
    },
    {
        # Test Case 3: The "Messy JD Experience" Text
        # Goal: Can the JD parser correctly extract the required years of experience from various common formats?
        "jd": {
            "skills": ["Java", "SQL", "Cloud"],
            "experience": ["Requires 5+ years with Java", "A minimum of 3 yrs experience with SQL", "2-4 years of cloud experience is a plus"]
        },
        "resume": {
            "Skills": ["Java", "SQL", "Cloud"],
            "Experience": { "Developer": ["Some Company", "2020-01", "2025-01", "5"] }
        }
    },
    {
        # Test Case 4: The "Complex Date Range" Experience in Resume
        # Goal: Can the resume parser handle and calculate durations from varied date formats? (This will be fully tested in Step 2, but we can check if it breaks the system now).
        "jd": {
            "skills": ["Project Management"]
        },
        "resume": {
            "Skills": ["Project Management"],
            "Experience": {
                "Project Lead": ["Corp A", "Jan 2020", "Present", ""],
                "Coordinator": ["Corp B", "August 2018", "December 2019", ""]
            }
        }
    },
    {
        # Test Case 5: The "Combined Mess" Test
        # Goal: A real-world test combining messy skill formats and varied JD experience requirements.
        "jd": {
            "skills": ["Python", "Pandas", "SQL", "Tableau"],
            "experience": ["4+ years in data analytics with Python"]
        },
        "resume": {
            "Skills": "Core skills: Python (pandas, numpy), SQL; also skilled in Tableau and PowerBI.",
            "Experience": { "Data Analyst": ["Data Inc.", "2020-01", "2025-01", "5"] }
        }
    }
]

# -------------------------
# Run Tests
# -------------------------
for idx, test_case in enumerate(normalization_test_cases, start=1):
    print(f"\n--- Running Normalization Test Case {idx} ---")
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