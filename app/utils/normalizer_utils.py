"""
Normalizer Utilities for Phase 2
--------------------------------
Helper functions for robust skill and experience normalization.
Includes:
- Skill splitting
- Date range parsing
- Duration calculation
- Logging of anomalies
- Skill normalization
"""

import re
import logging
from typing import List, Optional, Tuple
from dateutil import parser
from datetime import datetime

# -------------------------
# Logger Setup
# -------------------------
logger = logging.getLogger("normalizer_utils")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.FileHandler("logs/normalizer_utils.log")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# -------------------------
# Skill Synonyms Dictionary (from normalizer.py)
# -------------------------
SKILL_SYNONYMS = {
    # -- Programming Languages --
    'python': 'python',
    'py': 'python',
    'python3': 'python',
    'javascript': 'javascript',
    'js': 'javascript',
    'es6': 'javascript',
    'ecmascript': 'javascript',
    'vanilla js': 'javascript',
    'typescript': 'typescript',
    'ts': 'typescript',
    'java': 'java',
    'j2ee': 'java',
    'jee': 'java',
    'c++': 'c++',
    'cpp': 'c++',
    'c#': 'c#',
    'c sharp': 'c#',
    'dotnet': 'c#',
    'sql': 'sql',
    'structured query language': 'sql',
    't-sql': 'sql',
    'pl/sql': 'sql',
    'plsql': 'sql',
    'php': 'php',
    'ruby': 'ruby',
    'go': 'go',
    'golang': 'go',
    'swift': 'swift',
    'kotlin': 'kotlin',
    'rust': 'rust',
    'scala': 'scala',
    'r': 'r',
    'r language': 'r',
    'r programming': 'r',
    'powershell': 'powershell',
    'shell scripting': 'shell scripting',
    'bash': 'shell scripting',
    'shell script': 'shell scripting',
    'sh': 'shell scripting',

    # -- Frontend Frameworks & Libraries --
    'react': 'react',
    'react.js': 'react',
    'reactjs': 'react',
    'react native': 'react',
    'angular': 'angular',
    'angular.js': 'angular',
    'angularjs': 'angular',
    'vue.js': 'vue.js',
    'vue': 'vue.js',
    'vuejs': 'vue.js',
    'html': 'html',
    'html5': 'html',
    'css': 'css',
    'css3': 'css',
    'scss': 'css',
    'sass': 'css',
    'less': 'css',
    'tailwind css': 'css',
    'jquery': 'jquery',
    'bootstrap': 'bootstrap',
    'svelte': 'svelte',

    # -- Backend Frameworks & Libraries --
    'node.js': 'node.js',
    'node': 'node.js',
    'nodejs': 'node.js',
    'express': 'node.js',
    'express.js': 'node.js',
    'django': 'django',
    'django framework': 'django',
    'flask': 'flask',
    'spring boot': 'spring boot',
    'spring': 'spring boot',
    'spring framework': 'spring boot',
    'spring mvc': 'spring boot',
    'ruby on rails': 'ruby on rails',
    'rails': 'ruby on rails',
    'ror': 'ruby on rails',
    'laravel': 'laravel',
    'fastapi': 'fastapi',
    'fast api': 'fastapi',
    '.net core': 'c#',

    # -- Cloud & DevOps --
    'aws': 'aws',
    'amazon web services': 'aws',
    'gcp': 'gcp',
    'google cloud platform': 'gcp',
    'google cloud': 'gcp',
    'azure': 'azure',
    'microsoft azure': 'azure',
    'docker': 'docker',
    'containerization': 'docker',
    'kubernetes': 'kubernetes',
    'k8s': 'kubernetes',
    'ci/cd': 'ci/cd',
    'continuous integration': 'ci/cd',
    'continuous delivery': 'ci/cd',
    'jenkins': 'ci/cd',
    'github actions': 'ci/cd',
    'gitlab ci': 'ci/cd',
    'circleci': 'ci/cd',
    'terraform': 'terraform',
    'infrastructure as code': 'terraform',
    'iac': 'terraform',
    'ansible': 'ansible',
    'configuration management': 'ansible',
    'git': 'git',
    'version control': 'git',
    'github': 'git',
    'gitlab': 'git',
    'bitbucket': 'git',
    'linux': 'linux',
    'unix': 'linux',
    'ubuntu': 'linux',

    # -- Databases & Data Stores --
    'postgresql': 'postgresql',
    'postgres': 'postgresql',
    'pgsql': 'postgresql',
    'mysql': 'mysql',
    'mongodb': 'mongodb',
    'mongo': 'mongodb',
    'redis': 'redis',
    'sql server': 'sql server',
    'mssql': 'sql server',
    'microsoft sql server': 'sql server',
    'oracle': 'oracle',
    'oracle db': 'oracle',
    'sqlite': 'sqlite',
    'elasticsearch': 'elasticsearch',
    'cassandra': 'cassandra',
    'dynamodb': 'aws', # Often tied to AWS
    
    # -- Data Science & Machine Learning --
    'machine learning': 'machine learning',
    'ml': 'machine learning',
    'deep learning': 'deep learning',
    'dl': 'deep learning',
    'neural networks': 'deep learning',
    'natural language processing': 'natural language processing',
    'nlp': 'natural language processing',
    'computer vision': 'computer vision',
    'cv': 'computer vision',
    'data analysis': 'data analysis',
    'data analytics': 'data analysis',
    'pandas': 'pandas',
    'numpy': 'numpy',
    'scikit-learn': 'scikit-learn',
    'sklearn': 'scikit-learn',
    'tensorflow': 'tensorflow',
    'tf': 'tensorflow',
    'keras': 'tensorflow',
    'pytorch': 'pytorch',
    'torch': 'pytorch',
    'hugging face': 'hugging face transformers',
    'hugging face transformers': 'hugging face transformers',
    'apache spark': 'apache spark',
    'spark': 'apache spark',
    'pyspark': 'apache spark',
    'hadoop': 'hadoop',
    'data visualization': 'data visualization',
    'tableau': 'data visualization',
    'power bi': 'data visualization',
    'powerbi': 'data visualization',
    'matplotlib': 'data visualization',
    'seaborn': 'data visualization',
    'mlops': 'mlops',
    'ml ops': 'mlops',
    'mlflow': 'mlops',
    'kubeflow': 'mlops',
    'llm': 'llm',
    'large language models': 'llm',
    'openai': 'llm',
    'gpt': 'llm',
    'langchain': 'langchain',
    'rag': 'rag',
    'retrieval-augmented generation': 'rag',
    'vector database': 'vector database',
    'pinecone': 'vector database',
    'chroma': 'vector database',
    
    # -- Project Management & Methodologies --
    'agile': 'agile',
    'scrum': 'agile',
    'kanban': 'agile',
    'jira': 'jira',
    'atlassian jira': 'jira',
    'project management': 'project management',
    'pmp': 'project management',

    # -- Software & Design Tools --
    'figma': 'figma',
    'ui/ux design': 'figma',
    'wireframing': 'figma',
    'sketch': 'figma',
    'photoshop': 'photoshop',
    'adobe photoshop': 'photoshop',
    'illustrator': 'illustrator',
    'adobe illustrator': 'illustrator',
    'excel': 'excel',
    'microsoft excel': 'excel',
}
# -------------------------
# Skill Normalization
# -------------------------
def normalize_skill_name(skill: str) -> str:
    """
    Normalize skill names:
    - Lowercase, strip spaces, remove punctuation
    - Map synonyms from SKILL_SYNONYMS
    - Fallback partial matching
    - Log unknown skills for future dictionary updates
    """
    if not skill or not isinstance(skill, str):
        return ""

    # Clean skill string
    skill_clean = skill.strip().lower()
    skill_clean = re.sub(r"[^a-z0-9\s\+\#]", "", skill_clean)  # remove punctuation

    # Direct mapping
    if skill_clean in SKILL_SYNONYMS:
        return SKILL_SYNONYMS[skill_clean]

    # Partial match mapping
    for key, val in SKILL_SYNONYMS.items():
        if key in skill_clean:
            return val

    # Log unknown skill for review
    logger.info(f"Unknown skill detected: '{skill_clean}'")

    return skill_clean

# -------------------------
# Skill splitting
# -------------------------
def split_skill_string(raw_skill: str) -> List[str]:
    """
    Split a raw skill string into canonical list.
    Handles: comma, semicolon, pipe, 'and', sentence patterns like 'Skilled in X and Y'.
    Returns normalized, lowercased skills.
    """
    if not raw_skill or not isinstance(raw_skill, str):
        return []

    try:
        clean = re.sub(r'\(.*?\)', '', raw_skill).strip()
        parts = re.split(r'[;,|]', clean)
        skills = []
        for part in parts:
            sub_parts = re.split(r'\band\b', part, flags=re.I)
            for s in sub_parts:
                skill = normalize_skill_name(s.strip())
                if skill:
                    skills.append(skill)
        return skills
    except Exception as e:
        logger.error(f"[Skill Split] Failed to split '{raw_skill}': {e}")
        return []

# -------------------------
# Date parsing
# -------------------------
def parse_date_or_none(date_str: str) -> Optional[datetime]:
    if not date_str or not isinstance(date_str, str):
        return None
    try:
        return parser.parse(date_str)
    except Exception:
        logger.warning(f"[Date Parse] Could not parse date: '{date_str}'")
        return None

# -------------------------
# Duration calculation
# -------------------------
def compute_duration_in_years(start: Optional[datetime], end: Optional[datetime]) -> float:
    try:
        if not start:
            return 0.0
        if not end:
            end = datetime.now()
        delta = end - start
        years = delta.days / 365.25
        return round(years, 2)
    except Exception as e:
        logger.error(f"[Duration Calc] Failed for start={start}, end={end}: {e}")
        return 0.0

# -------------------------
# Experience string parsing (JD)
# -------------------------
def parse_experience_string(exp_str: str) -> Tuple[float, List[str]]:
    if not exp_str or not isinstance(exp_str, str):
        return 0.0, []

    try:
        match = re.search(r'(\d+)(?:\s*-\s*(\d+))?\+?\s*(?:yrs?|years?)', exp_str, re.IGNORECASE)
        if match:
            start_years = int(match.group(1))
            end_years = int(match.group(2)) if match.group(2) else start_years
            duration = float(end_years)
        else:
            duration = 0.0

        skill_match = re.search(r'(?:in|of|with)?\s*([\w\s\+\#&]+)', exp_str, re.IGNORECASE)
        skill_str = skill_match.group(1).strip() if skill_match else ""
        skills = split_skill_string(skill_str)
        return duration, skills
    except Exception as e:
        logger.error(f"[JD Exp Parse] Failed to parse '{exp_str}': {e}")
        return 0.0, []

# -------------------------
# Misc helpers
# -------------------------
def sanitize_string(s: str) -> str:
    if not s or not isinstance(s, str):
        return ""
    try:
        s_clean = s.strip().lower()
        s_clean = re.sub(r"[^a-z0-9\s\+\#]", "", s_clean)
        return s_clean
    except Exception as e:
        logger.error(f"[Sanitize String] Failed for '{s}': {e}")
        return ""