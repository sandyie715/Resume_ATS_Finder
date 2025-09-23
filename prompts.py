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
