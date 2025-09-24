class ResumePrompt:
    base_prompt = """
You are a JSON generator. 
Strictly return ONLY valid JSON (no explanations, no markdown, no extra text).

Extract the following information from the resume text below:

{resume_text}

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

class JDPrompt:
    base_prompt = (
        "You are an expert recruiter parsing Job Descriptions.\n"
        "Given the JD below, extract:\n"
        "1) 'skills' — a concise list of required or strongly preferred skills/technologies.\n"
        "2) 'experience' — any explicit experience requirements (years + skill or domain), "
        "as short phrases (e.g. '4 years in Python', '2+ years in analytics').\n\n"
        "Output ONLY a JSON object. Do NOT add commentary or any extra text.\n\n"
        "JD:\n\n\"\"\"\n{jd_text}\n\"\"\"\n\n"
        "Return the JSON object now."
    )

