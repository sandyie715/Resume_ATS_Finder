import subprocess
import re
import json
from prompts import ResumePrompt
from utils.logger import logger
from constants import OLLAMA_MODEL

def extract_resume_info(text):
    prompt_text = ResumePrompt.base_prompt.format(resume_text=text)
    try:
        result = subprocess.run(
            ["ollama", "run", OLLAMA_MODEL],
            input=prompt_text,
            capture_output=True,
            text=True,
            encoding="utf-8",  
            errors="ignore" 
        )
        response = result.stdout.strip()

        # Extract JSON only
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            response = match.group(0)

        data = json.loads(response)
        logger.info("Resume JSON extracted successfully")
        return data
    except Exception as e:
        logger.error(f"Failed to extract resume info: {str(e)}")
        return {
            "error": f"Failed to parse JSON: {str(e)}",
            "raw_output": response if 'response' in locals() else ""
        }
        
        
