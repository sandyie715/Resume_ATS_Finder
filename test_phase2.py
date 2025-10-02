import requests
import json

# Replace with your local API URL
API_URL = "http://127.0.0.1:8000/similarity"

# -------------------------
# Test Cases
# -------------------------
test_cases = [
    {
        "resume": {
            "Name": ["Sanjay D K"],
            "Profile Title": "AI Engineer with hands-on experience in designing, building, and deploying end-to-end machine learning systems.",
            "Email": "",
            "Contact": {
                "Primary number": ["India"],
                "Secondary number": ["Country code: IN"]
            },
            "Gender": "Male",
            "Date of Birth": "2024-08-20",
            "Address": {
                "Address Line1": "Mangalore",
                "Address Line2": "",
                "Country": "India",
                "State": "Karnataka",
                "City": "Mangalore",
                "Postal Code": "India"
            },
            "Total Years Experience": "6",
            "Nationality": "India",
            "GitHub Link": "",
            "Website/Portfolio": "",
            "Skills": [
                "Python", "MLOps", "AWS", "GCP", "Deep Learning",
                "TensorFlow", "PyTorch", "Keras", "Scikit-learn"
            ],
            "Experience": {
                "First working company name": ["Sankhya Association"],
                "Role": "Vice President",
                "Start Date": "2023-08",
                "End Date": "2024-08",
                "Total years experience": "5"
            },
            "Projects": [
                {
                    "Name": "Predictive Analytics for Employee Retention",
                    "Description": "Full-Cycle MLOps Workflow",
                    "GitHub": "sandyie.in/ml/HRAnlytics",
                    "Accuracy": "89%",
                    "Automation": "80%"
                },
                {
                    "Name": "Project",
                    "Description": "CustomerEngagementPridection",
                    "GitHub": "RecommendationSystem",
                    "Accuracy": "90%",
                    "Improvements": "Reduced query latency by 30%"
                },
                {
                    "Name": "Serverless RAG Chatbot",
                    "Description": "End-to-End LLMOpsCI/CD Pipeline",
                    "GitHub": "sandyie.in/ml/HRAnlytics",
                    "LatencyReduction": "30%"
                }
            ]
        },
        "jd": {
            "skills": [
                "Python", "JavaScript", "TensorFlow", "PyTorch",
                "Hugging Face Transformers", "LLM Integration",
                "OpenAI/GPT-4 APIs", "LangChain", "VectorDBs (Pinecone, Chroma)",
                "GitHub", "Docker", "REST APIs", "AWS/GCP basics",
                "MLflow", "Weights & Biases", "Prompt Engineering"
            ]
        }
    }
]

# -------------------------
# Run Tests
# -------------------------
for idx, test_case in enumerate(test_cases, start=1):
    print(f"\n--- Running Test Case {idx} ---")
    try:
        response = requests.post(API_URL, json=test_case)
        if response.status_code == 200:
            print("Response JSON:")
            print(json.dumps(response.json(), indent=4))
        else:
            print(f"FAILED with status code {response.status_code}")
            print("Response Text:")
            print(response.text)
    except requests.exceptions.ConnectionError as e:
        print(f"FAILED: Could not connect to the API at {API_URL}.")
        print("Please ensure your FastAPI server is running.")
        break