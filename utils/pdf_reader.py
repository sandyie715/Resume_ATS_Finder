import pdfplumber
import os
from docx import Document
from utils.logger import logger
import re

def normalize_text(text : str = None) -> str :
    """
    Args : 
        string : It accepts resume in string/text format
    
    return :
        Normalize extracted text:
        - Remove extra whitespace and newlines
        - Remove non-printable characters
        - Collapse multiple spaces into one
    """
    if not text:
        return ""
    
    # Remove non-printable characters
    text = re.sub(r'[^\x20-\x7E\n]', ' ', text)
    # Replace multiple newlines with single newline
    text = re.sub(r'\n+', '\n', text)
    # Replace multiple spaces/tabs with single space
    text = re.sub(r'[ \t]+', " ", text)
    # Strip leading/trailing spaces
    text = text.strip()
    return text

def read_pdf(file_path : str = None) -> str:
    """
    Desc : 
        It reads pdf files format files only.

    Args : 
        file_path (string) : The path of the file.

    Return :
        string : Returns pdf content into normalized string format.
    """
    try: 
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        logger.info(f"PDF read successfully: {file_path}")
        return normalize_text(text)

    except Exception as e:
        logger.error(f"Error reading PDF {file_path}: {str(e)}")
        return ""

def read_docx(file_path: str = None) -> str:
    """
    Desc : 
        It reads docs files format files only.

    Args : 
        file_path (string) : The path of the file.

    Return :
        string : Returns docs content into normalized string format.
    """
    try:
        doc = Document(file_path) 
        text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        logger.info(f"DOCX read successfully : {file_path}")
        return normalize_text(text)
    except Exception as e : 
        logger.error(f"Error reading DOCX {file_path} : {str(e)}")
        return ""

def read_txt(file_path :str = None)-> str: 
    """
    Desc : 
        It reads text files format files only.

    Args : 
        file_path (string) : The path of the file.

    Return :
        string : Returns text content into normalized string format.
    """
    try:
        with open(file_path, "r", encoding= "utf-8") as f:
            text = f.read()
        logger.info(f"TXT read successfully : {file_path}")
        return normalize_text(text)
    except Exception as e:
        logger.error(f"Error reading TXT {file_path} : {str(e)}")
        return ""

def read_resume(file_path: str = None) -> str:
    """
    Desc :
        Detect file type and extract text.
        support PDF, DOCX, TXT
    Args :
        file_path (string) : The path of the file.
    
    Return:
        String : Returns text content into normalized string format.
    """
    ext = os.path.splittext(file_path)[1].lower()
    if ext == ".pdf":
        return read_pdf(file_path)
    elif ext == ".docx":
        return read_docx(file_path)
    elif ext == ".txt":
        return read_txt(file_path)
    else:
        logger.error(f"Unsupported file format : {ext}")
        return ""