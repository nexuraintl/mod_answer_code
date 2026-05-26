import os
import json
import requests
from config import Config
from src.models.errors import AppError

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise AppError("GEMINI_API_KEY no configurada", "CONFIG_ERROR", 500)

    def answer(self, prompt: str) -> dict:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{Config.GEMINI_MODEL}:generateContent"
        params = {"key": self.api_key}

        body = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.5, "maxOutputTokens": 1500},
        }

        r = requests.post(url, params=params, json=body, timeout=45)
        if r.status_code >= 400:
            raise AppError(f"Gemini call failed: {r.status_code} {r.text}", "GEMINI_ERROR", 502)

        data = r.json()
        text = self._extract_text(data)
        text = self._strip_fences(text)

        parsed = None
        try:
            parsed = json.loads(text)
        except Exception:
            parsed = None

        return {
            "model": Config.GEMINI_MODEL,
            "raw_text": text,
            "parsed": parsed,
            "answer": parsed.get("answer") if isinstance(parsed, dict) and "answer" in parsed else text,
        }

    def _strip_fences(self, s: str) -> str:
        if not s:
            return ""
        t = s.strip()
        if t.startswith("```"):
            t = t.split("\n", 1)[1] if "\n" in t else t
            if t.endswith("```"):
                t = t[:-3]
        return t.strip()

    def _extract_text(self, data: dict) -> str:
        cands = data.get("candidates") or []
        if not cands:
            return ""
        parts = (((cands[0].get("content") or {}).get("parts")) or [])
        out = []
        for p in parts:
            if isinstance(p, dict) and p.get("text"):
                out.append(p["text"])
        return "".join(out).strip()
    
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """
        Genera embeddings usando la API de Google Generative Language.
        Devuelve una lista de vectores (float).
        """
        texts = [t.strip() for t in (texts or []) if isinstance(t, str) and t.strip()]
        if not texts:
            return []

        # Modelo de embeddings configurable
        embed_model = os.getenv("GEMINI_EMBED_MODEL", "text-embedding-004")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{embed_model}:batchEmbedContents"
        params = {"key": self.api_key}

        body = {
            "requests": [{"content": {"parts": [{"text": t}]}} for t in texts]
        }

        r = requests.post(url, params=params, json=body, timeout=45)
        if r.status_code >= 400:
            # fallback a otro modelo común (por si el primero no está habilitado)
            fallback_model = os.getenv("GEMINI_EMBED_FALLBACK", "embedding-001")
            if fallback_model and fallback_model != embed_model:
                url2 = f"https://generativelanguage.googleapis.com/v1beta/models/{fallback_model}:batchEmbedContents"
                r2 = requests.post(url2, params=params, json=body, timeout=45)
                if r2.status_code < 400:
                    data2 = r2.json()
                    return self._extract_embeddings(data2)
            return []

        data = r.json()
        return self._extract_embeddings(data)

    def _extract_embeddings(self, data: dict) -> list[list[float]]:
        out: list[list[float]] = []
        embeddings = data.get("embeddings") or []
        for e in embeddings:
            vals = (e.get("values") if isinstance(e, dict) else None)
            if isinstance(vals, list) and vals:
                out.append(vals)
        return out

