import pdfplumber
import json
import subprocess
import re
from keybert import KeyBERT

# -------------------------------
# 1️⃣ Read PDF and extract text
# -------------------------------
def read_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

# -------------------------------
# 2️⃣ Extract skills using KeyBERT
# -------------------------------
def extract_skills(text):
    kw_model = KeyBERT(model='distilbert-base-nli-mean-tokens')
    keywords = kw_model.extract_keywords(
        text,
        keyphrase_ngram_range=(1, 2),
        stop_words='english',
        top_n=20
    )
    skills = [kw[0] for kw in keywords]
    return skills

# -------------------------------
# 3️⃣ Extract structured resume info using Ollama CLI
# -------------------------------
def extract_resume_info(text):
    prompt_text = f"""
You are a JSON generator. 
Strictly return ONLY valid JSON (no explanations, no markdown, no extra text).

Extract the following information from the resume text below:

{text}

Format:
{{
  "Name": ["First name", "Last Name"],
  "Profile Title": "",
  "Email": "",
  "Contact": {{
    "Primary number": ["Country code", "Number"],
    "Secondary number": ["Country code", "Number"]
  }},
  "Gender": "",
  "Date of Birth": "Date format",
  "Address": {{
    "Address Line1": "",
    "Address Line2": "",
    "Country": "",
    "State": "",
    "City": "",
    "Postal Code": ""
  }},
  "Total Years Experience": "",
  "Nationality": "",
  "GitHub Link": "",
  "Website/Portfolio": "",
  "LinkedIn Link": "",
  "Education": {{
    "First college": ["college name", "studied year", "marks/cgpa/score"]
  }},
  "Skills": [],
  "Experience": {{
    "First working company name": ["Role", "Start Date", "End Date", "total years experience"]
  }},
  "Project": {{
    "Project1 name": ["Start Date", "End Date", ["skills used"]]
  }}
}}
"""

    try:
        result = subprocess.run(
            ["ollama", "run", "mistral:7b"],  # ⚡ changed "prompt" → "run"
            input=prompt_text,
            capture_output=True,
            text=True
        )
        response = result.stdout.strip()

        # ⚡ Extract only JSON part (sometimes model adds text)
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            response = match.group(0)

        data = json.loads(response)
    except Exception as e:
        data = {
            "error": f"Failed to parse JSON: {str(e)}",
            "raw_output": response if 'response' in locals() else ""
        }
    return data

# -------------------------------
# 4️⃣ Combine skills from KeyBERT
# -------------------------------
def combine_skills(resume_json, keybert_skills):
    resume_json['Skills'] = keybert_skills
    return resume_json

# -------------------------------
# 5️⃣ Main function
# -------------------------------
if __name__ == "__main__":
    pdf_path = "Karunasagara_TM.pdf"  # Replace with your resume PDF
    text = read_pdf(pdf_path)
    keybert_skills = extract_skills(text)
    resume_json = extract_resume_info(text)
    final_json = combine_skills(resume_json, keybert_skills)

    # ⚡ Pretty print with indent
    print(json.dumps(final_json, indent=4, ensure_ascii=False))