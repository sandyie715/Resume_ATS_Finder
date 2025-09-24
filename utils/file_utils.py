import json
from constants import JSON_OUTPUT_FILE
from utils.logger import logger

def save_json(data, file_path=JSON_OUTPUT_FILE):
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        logger.info(f"JSON saved successfully: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Error saving JSON: {str(e)}")
        return None

