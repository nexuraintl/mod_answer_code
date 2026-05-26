import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Azure DevOps
    AZURE_PAT = os.getenv("AZURE_PAT", "")
    AZURE_ORG_URL = os.getenv("AZURE_ORG_URL", "").rstrip("/")
    
    azure_repos_raw = os.getenv("AZURE_CORE_REPOS", "")
    AZURE_CORE_REPOS = [x.strip() for x in azure_repos_raw.split(",") if x.strip()]
    
    AZURE_USE_CODE_SEARCH = os.getenv("AZURE_USE_CODE_SEARCH", "true").lower() == "true"
    AZDO_DEFAULT_BRANCH = os.getenv("AZDO_DEFAULT_BRANCH", "main")

    # Gemini
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "models/gemini-2.0-flash")

    # Límites
    MAX_REPOS = int(os.getenv("MAX_REPOS", "2"))
    MAX_FILES = int(os.getenv("MAX_FILES", "15"))
    MAX_FILE_BYTES = int(os.getenv("MAX_FILE_BYTES", "120000"))
    MAX_CONTEXT_CHARS = int(os.getenv("MAX_CONTEXT_CHARS", "20000"))

    # Extensiones permitidas
    ALLOWED_EXT = (
    ".py", ".java", ".ts", ".js", ".go", ".cs", ".rb", ".php", ".sql",".conf", ".nginx", ".inc"
    )
