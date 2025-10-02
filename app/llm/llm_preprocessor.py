# app/llm/llm_preprocessor.py

import json
import logging
from typing import Dict, Any
from pydantic import BaseModel, ValidationError, Field
import ollama  # ✅ Using ollama library directly

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# -------------------------------
# LLM Client Configuration
# -------------------------------
MODEL_NAME = "llama3.2:3b"  # ✅ Updated model name

# -------------------------------
# Schemas for structured output
# -------------------------------
class ExperienceItem(BaseModel):
    skill: str
    years: float = Field(ge=0)

class PhaseOutput(BaseModel):
    skills: list[str] = Field(default_factory=list)
    experience: list[ExperienceItem] = Field(default_factory=list)

class LLMOutputSchema(BaseModel):
    resume: PhaseOutput
    jd: PhaseOutput

# -------------------------------
# Exceptions
# -------------------------------
class LLMPreprocessorError(Exception):
    pass

# -------------------------------
# Prompt Builder
# -------------------------------
def build_prompt(raw_json: Dict[str, Any]) -> str:
    """
    Build a robust normalization prompt for the LLM.
    """
    return f"""
You are a highly precise data normalization engine. Your sole task is to convert the raw JSON below into a single valid JSON object with exactly this schema:

{{
  "resume": {{
    "skills": [],
    "experience": []
  }},
  "jd": {{
    "skills": [],
    "experience": []
  }}
}}

## Important Rules:

1. Output ONLY JSON. No markdown, backticks, explanations, or placeholders.
2. Skills Normalization:
   - Extract all skills from any input format.
   - Split on commas ',', semicolons ';', pipes '|', and slashes '/'.
   - Expand parentheses. Example: "Python (Pandas, NumPy)" → "python","pandas","numpy".
   - Lowercase all skill names.
   - Remove duplicates and sort alphabetically.
3. Experience Normalization:
   - JD: Convert strings like "5+ years of experience with Java" → {{"skill":"java","years":5.0}}.
   - Resume: Compute years from start and end dates. If end date is "Present", assume 2025.
   - Years must be numeric literals only. No calculations or expressions.
   - Skills in experience must exactly match normalized skills.
4. Strict JSON Enforcement:
   - Must parse with standard JSON parsers.
   - No extra fields beyond 'resume' and 'jd'.
   - No empty skill names. Years must be ≥ 0.
5. Do not use Markdown, quotes around JSON keys, or any formatting other than raw JSON.

## Raw Input JSON:
{json.dumps(raw_json, indent=2)}

## Only output the final JSON object exactly as above.
"""

# -------------------------------
# LLM Call
# -------------------------------
def call_llm_api(prompt: str) -> str:
    """
    Call local LLM via ollama.chat and return raw text output.
    """
    try:
        logger.info("Calling local LLM via ollama.chat for normalization...")
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}]
        )
        text_output = response["message"]["content"].strip()

        print("\n===== RAW LLM OUTPUT FROM ollama.chat =====")
        print(text_output)
        print("===== END RAW LLM OUTPUT =====\n")

        if not text_output:
            raise LLMPreprocessorError("LLM returned empty response.")
        return text_output

    except Exception as e:
        raise LLMPreprocessorError(f"Unexpected LLM error: {str(e)}")

# -------------------------------
# Key Normalization Utility
# -------------------------------
def normalize_keys(d):
    """
    Convert all dictionary keys to lowercase recursively.
    """
    if isinstance(d, dict):
        return {k.lower(): normalize_keys(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [normalize_keys(i) for i in d]
    else:
        return d

# -------------------------------
# Post-Processing for LLM Output
# -------------------------------
def postprocess_llm_output(obj: dict) -> dict:
    """
    Clean minor inconsistencies in LLM output.
    Ensures skills are strings, experiences have numeric years, and known typos fixed.
    """
    def clean_skill(skill) -> str:
        if not isinstance(skill, str):
            skill = str(skill)
        skill = skill.strip().lower()
        skill = skill.replace("skikit-learn", "scikit-learn")
        return skill

    def clean_experience(exp_list):
        cleaned = []
        if not isinstance(exp_list, list):
            return cleaned
        for item in exp_list:
            if not isinstance(item, dict):
                continue
            skill = clean_skill(item.get("skill", ""))
            years = item.get("years", 0)
            try:
                years = float(years)
            except Exception:
                years = 0.0
            if skill and years >= 0:
                cleaned.append({"skill": skill, "years": years})
        return cleaned

    for key in ["resume", "jd"]:
        if key in obj:
            skills = obj[key].get("skills", [])
            obj[key]["skills"] = sorted({clean_skill(s) for s in skills if s})
            obj[key]["experience"] = clean_experience(obj[key].get("experience", []))
    return obj

# -------------------------------
# LLM Output Parsing
# -------------------------------
def parse_llm_output(text: str) -> dict:
    """
    Parse LLM output JSON with robust error handling.
    """
    text = text.strip()

    # Strip code fences if LLM returns ```json ... ```
    if text.startswith("```json"):
        text = text[len("```json"):].strip()
    elif text.startswith("```"):
        text = text[3:].strip()
    if text.endswith("```"):
        text = text[:-3].strip()

    text = text.strip()
    decoder = json.JSONDecoder()
    try:
        obj, idx = decoder.raw_decode(text)
        obj = normalize_keys(obj)
        obj = postprocess_llm_output(obj)
        validated = LLMOutputSchema(**obj)
        return validated.dict()
    except (json.JSONDecodeError, ValidationError, TypeError) as e:
        raise LLMPreprocessorError(f"LLM output parsing/validation failed: {e}")

# -------------------------------
# Main Preprocessor
# -------------------------------
def preprocess_with_llm(raw_json: Dict[str, Any]) -> Dict[str, Any]:
    prompt = build_prompt(raw_json)
    try:
        raw_output = call_llm_api(prompt)
        structured_output = parse_llm_output(raw_output)
        logger.info("✅ LLM preprocessing successful.")
        return structured_output
    except LLMPreprocessorError as e:
        logger.error(f"LLM preprocessing failed: {e}")
        return raw_json  # fallback

# -------------------------------
# Helper Wrappers
# -------------------------------
def llm_normalize_jd(raw_jd: dict) -> dict:
    return preprocess_with_llm({"jd": raw_jd})["jd"]

def llm_normalize_resume(raw_resume: dict) -> dict:
    return preprocess_with_llm({"resume": raw_resume})["resume"]