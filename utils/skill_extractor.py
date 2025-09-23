from keybert import KeyBERT
from constants import KEYBERT_MODEL, TOP_N_KEYWORDS, STOP_WORDS
from utils.logger import logger

def extract_skills(text:  str| None = None) -> list[str]:
    """
    Extract skills from the given text.

    Agrs:
        text (string | None) : Input text (e.g. , resume content).
                                Defaults to None.
    Returns :
        list[str] : A list of extracted skills as strings.
    """
    try :
        kw_model = KeyBERT(model = KEYBERT_MODEL)
        keywords = kw_model.extract_keywords(
            text,
            keyphrase_ngram_range = (1, 2),
            stop_words = STOP_WORDS,
            top_n = TOP_N_KEYWORDS
        )
        skills = [kw[0] for kw in keywords]
        logger.info(f"Extracted {len(skills)} skills using KeyBERT")
        return skills


    except Exception as e:
        logger.error(f"Error extracting skills : {str(e)}")
        return []
    
    
