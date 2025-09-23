import logging

"""
usage : 
    from resume_parser_logger import logger
    logger.info("THis is an informational message.")
"""

def setup_logger():
    """
    Args : 
        Nothing
    desc :
        Sets up and returns a configured logger for the resume parser.
    
    Returns :
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger("resume_parser")
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger

logger = setup_logger()