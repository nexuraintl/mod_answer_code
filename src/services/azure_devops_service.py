import base64
import requests
from urllib.parse import quote, urlparse
from config import Config
from src.models.errors import AppError


class AzureDevOpsService:
    """
    configuracion de servicio Azure DevOps
    """

    def __init__(self):
        if not Config.AZURE_PAT:
            raise AppError("AZURE_PAT no  configurado", "CONFIG_ERROR", 500)       


        org_url_raw = (Config.AZURE_ORG_URL or "").strip()
        if not org_url_raw:
            raise AppError(
                "AZURE_ORG_URL not configured. Use https://dev.azure.com/ORG o https://ORG.visualstudio.com",
                "CONFIG_ERROR",
                500,
            )

        self.org_url = self._normalize_org_url(org_url_raw)
        token = f":{Config.AZURE_PAT}".encode("utf-8")
        b64 = base64.b64encode(token).decode("utf-8")
        self.headers = {
            "Authorization": f"Basic {b64}",
            "Content-Type": "application/json",
        }

        self.default_branch = Config.AZDO_DEFAULT_BRANCH or "main"


    def _normalize_org_url(self, org_url: str) -> str:
        """
        Normalización de URL base
        """
        if not org_url.startswith("http://") and not org_url.startswith("https://"):
            org_url = "https://" + org_url
        parsed = urlparse(org_url)
        if not parsed.netloc:
            raise AppError("Invalid AZURE_ORG_URL format", "CONFIG_ERROR", 500)

        if "dev.azure.com" in parsed.netloc:
            parts = parsed.path.strip("/").split("/")
            if not parts or not parts[0]:
                raise AppError(
                    "Invalid AZURE_ORG_URL format for dev.azure.com. Expected https://dev.azure.com/ORG",
                    "CONFIG_ERROR",
                    500,
                )
            return f"https://{parsed.netloc}/{parts[0]}"

        return f"https://{parsed.netloc}"


    def _get(self, url: str, params: dict | None = None):
        r = requests.get(url, headers=self.headers, params=params, timeout=45)
        if r.status_code >= 400:
            body_preview = (r.text or "")[:600]
            raise AppError(f"Azure GET failed: {r.status_code} {body_preview}", "AZURE_ERROR", 502)
        ctype = (r.headers.get("Content-Type") or "").lower()
        if "application/json" in ctype:
            return r.json()
        return r.text

    def _enc_project(self, project: str) -> str:
        
        return quote(project, safe="")

    def _enc_repo(self, repo: str) -> str:
        return quote(repo, safe="")

    
    # API: Code Search     
    def search_code(self, project: str, repo: str, search_text: str, top: int = 25):
        project_enc = self._enc_project(project)
        url = f"{self.org_url}/{project_enc}/_apis/search/codesearchresults?api-version=7.1-preview.1"
        body = {
            "searchText": search_text,
            "filters": {"Repository": [repo]},
            "$top": int(top),
        }
        return self._post(url, body)

    def list_items(self, project: str, repo: str):
        """
        Lista árbol del repositorio (paths). Fallback cuando no hay Code Search.
        """
        project_enc = self._enc_project(project)
        repo_enc = self._enc_repo(repo)

        url = f"{self.org_url}/{project_enc}/_apis/git/repositories/{repo_enc}/items"
        params = {
            "recursionLevel": "Full",
            "includeContentMetadata": "true",
            "api-version": "7.1",
        }
        return self._get(url, params=params)

    def get_file_content(self, project: str, repo: str, path: str) -> tuple[str, dict]:
        project_enc = self._enc_project(project)
        repo_enc = self._enc_repo(repo)

        url = f"{self.org_url}/{project_enc}/_apis/git/repositories/{repo_enc}/items"

        params = {
            "path": path,
            "versionDescriptor.version": self.default_branch,  
            "versionDescriptor.versionType": "branch",
            "includeContent": "true",
            "api-version": "7.1",
        }

        resp = self._get(url, params=params)

        if isinstance(resp, dict):
            content = resp.get("content") or ""
            return content, {"mode": "json", "path": path}
        return str(resp or ""), {"mode": "text", "path": path}


