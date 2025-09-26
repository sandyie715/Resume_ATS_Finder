import json
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

if __name__ == "__main__":
    with open("resume_output.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    raw_output = data["raw_output"]
    fixed_json_str = clean_and_fix_json(raw_output)
    try:
        parsed = json.loads(fixed_json_str)
        with open("cleaned_resume_output.json", "w", encoding="utf-8") as f:
            json.dump(parsed, f, indent=2, ensure_ascii=False)
        print("Cleaned and fixed resume output saved to cleaned_resume_output.json")
    except Exception as e:
        print(f"Error parsing cleaned JSON: {e}")
