# utils/jd_extractor.py
import subprocess
import re
import json
from json.decoder import JSONDecodeError
from prompts import JDPrompt
from utils.logger import logger

OLLAMA_MODEL = "gemma3:1b"  # use the gemma3:1b model as requested

def _safe_json_loads(text: str):
    """Attempt json.loads and try minor repairs (remove trailing commas)."""
    try:
        return json.loads(text)
    except JSONDecodeError:
        # common repairs: trailing commas inside objects/arrays
        repaired = re.sub(r",\s*([}\]])", r"\1", text)
        try:
            return json.loads(repaired)
        except Exception as e:
            logger.error(f"JSON repair failed: {e}")
            return None

def extract_jd_info(jd_text: str) -> dict:
    """
    Call the LLM prompt to extract skills and experience from JD text.
    Returns a dict with keys 'skills' and optional 'experience'.
    If parsing fails, returns {'error': ..., 'raw_output': '...'}
    """
    prompt = JDPrompt.base_prompt.format(jd_text=jd_text)
    try:
        result = subprocess.run(
            ["ollama", "run", OLLAMA_MODEL],
            input=prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )
        response = (result.stdout or "").strip()
        # Extract the first JSON object found
        match = re.search(r"\{[\s\S]*\}", response)
        if match:
            json_text = match.group(0)
        else:
            json_text = response  # try whole output

        data = _safe_json_loads(json_text)
        if data is None:
            raise ValueError("Failed to parse JSON from model output")

        # Normalize output: ensure 'skills' exists as list
        skills = data.get("skills", [])
        if not isinstance(skills, list):
            skills = [skills] if skills else []

        out = {"skills": skills}
        experience = data.get("experience", None)
        if experience:
            # ensure list if string found
            if isinstance(experience, list):
                out["experience"] = experience
            else:
                out["experience"] = [experience]

        logger.info(f"Extracted JD: {len(out['skills'])} skills, experience present: {'experience' in out}")
        return out

    except Exception as e:
        logger.error(f"Failed to extract JD info: {e}")
        return {
            "error": f"Failed to extract JD info: {str(e)}",
            "raw_output": response if 'response' in locals() else ""
        }
