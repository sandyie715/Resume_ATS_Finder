# app.py
from fastapi import FastAPI, UploadFile, File, Request, Form
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
import shutil
import os
import json

from utils.pdf_reader import read_resume       # Auto-detect PDF/DOCX/TXT
#from utils.skill_extractor import extract_skills, combine_skills
from utils.resume_parser import extract_resume_info
from utils.file_utils import save_json
from utils.logger import logger
from utils.jd_extractor import extract_jd_info
from utils.similarity import jd_resume_similarity
from utils.scoring import calculate_match_score
from constants import JSON_OUTPUT_FILE

# Additional file paths for JD and combined outputs
JD_OUTPUT_FILE = "jd_output.json"
COMBINED_OUTPUT_FILE = "combined_output.json"

# ------------------------
# FastAPI initialization
# ------------------------
app = FastAPI(title="Resume Parser API")

# Template setup (serves index.html in the project root)
templates = Jinja2Templates(directory=".")

# Folder for uploaded files
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def home(request: Request):
    """Home route - renders index.html (upload form + JD paste area)"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload_resume/")
async def upload_resume(file: UploadFile = File(...)):
    """Upload endpoint: process uploaded resume file and save resume JSON."""
    try:
        # Save uploaded file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        logger.info(f"Uploaded file saved at: {file_path}")

        # Extract text from uploaded file (auto-detect format)
        text = read_resume(file_path)
        if not text:
            return {"error": "Failed to extract text from the uploaded resume."}

        # Extract skills (KeyBERT) and structured resume (LLM)
        #keybert_skills = extract_skills(text)
        resume_json = extract_resume_info(text)

        # Merge skills
        #final_json = combine_skills(resume_json, keybert_skills)

        # Save resume JSON output
        save_json(resume_json, file_path=JSON_OUTPUT_FILE)

        return {
            "message": "Resume processed successfully",
            "download_url": "/download_json/"
        }

    except Exception as e:
        logger.error(f"Error in upload_resume endpoint: {str(e)}")
        return {"error": str(e)}


@app.post("/process_jd/")
async def process_jd(jd_text: str = Form(...)):
    """
    Process pasted JD text from frontend:
    - Extract skills & experience using Ollama gemma3:1b via utils.jd_extractor
    - Save jd_output.json
    - Combine with resume JSON (resume JSON must exist) and save combined_output.json
    """
    try:
        jd_json = extract_jd_info(jd_text)
        # Save JD JSON
        save_json(jd_json, file_path=JD_OUTPUT_FILE)

        # Try to load resume JSON if exists
        resume_data = {}
        if os.path.exists(JSON_OUTPUT_FILE):
            try:
                with open(JSON_OUTPUT_FILE, "r", encoding="utf-8") as f:
                    resume_data = json.load(f)
            except Exception as e:
                logger.error(f"Error loading resume JSON for combination: {e}")
                resume_data = {}

        combined = {
            "resume": resume_data,
            "jd": jd_json
        }
        save_json(combined, file_path=COMBINED_OUTPUT_FILE)

        return {
            "message": "JD processed and combined successfully",
            "download_url": "/download_combined/"
        }

    except Exception as e:
        logger.error(f"Error in process_jd endpoint: {e}")
        return {"error": str(e)}


@app.get("/download_json/")
def download_json():
    """Download the processed resume JSON file"""
    if os.path.exists(JSON_OUTPUT_FILE):
        return FileResponse(JSON_OUTPUT_FILE, filename=os.path.basename(JSON_OUTPUT_FILE))
    else:
        return {"error": "JSON file not found."}


@app.get("/download_combined/")
def download_combined():
    """Download the combined resume + jd JSON"""
    if os.path.exists(COMBINED_OUTPUT_FILE):
        return FileResponse(COMBINED_OUTPUT_FILE, filename=os.path.basename(COMBINED_OUTPUT_FILE))
    else:
        return {"error": "Combined JSON file not found."}


# New endpoint to serve cleaned resume output

# Integrated cleaning and fixing logic
import re

def clean_and_fix_json(raw_json_str):
    # Remove recursive 'Format' fields (if present)
    cleaned = re.sub(r'"Format":\s*{.*?"Format":\s*{.*?}\s*}', '', raw_json_str, flags=re.DOTALL)
    # Remove any trailing commas before closing braces/brackets
    cleaned = re.sub(r',\s*([}\]])', r'\1', cleaned)
    # Replace problematic key '["skills used"]' with 'skills used'
    cleaned = re.sub(r'"\[\\"skills used\\"\]":', '"skills used":', cleaned)
    # Replace any other keys with brackets (e.g., ["key"]) with just "key"
    cleaned = re.sub(r'"\[\\"(.*?)\\"\]":', r'"\1":', cleaned)
    return cleaned

@app.get("/download_cleaned_resume/")
def download_cleaned_resume():
    """Generate and download the cleaned resume output JSON file on demand"""
    resume_output_file = "resume_output.json"
    cleaned_file = "cleaned_resume_output.json"
    if not os.path.exists(resume_output_file):
        return {"error": "resume_output.json not found."}
    try:
        with open(resume_output_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        raw_output = data.get("raw_output", "")
        fixed_json_str = clean_and_fix_json(raw_output)
        parsed = json.loads(fixed_json_str)
        with open(cleaned_file, "w", encoding="utf-8") as f:
            json.dump(parsed, f, indent=2, ensure_ascii=False)
        return FileResponse(cleaned_file, filename=os.path.basename(cleaned_file))
    except Exception as e:
        return {"error": f"Error cleaning resume JSON: {e}"}


@app.get("/similarity/")
def get_similarity():
    """
    Endpoint: returns similarity score + missing skills
    """
    try:
        results = jd_resume_similarity("combined_output.json")
        return results
    except Exception as e:
        return {"error": str(e)}

@app.get("/score/")
def get_match_score():
    """
    Endpoint: returns a match score (0-100) based on skills and experience
    """
    try:
        score = calculate_match_score("combined_output.json")
        return {"match_score": score}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
