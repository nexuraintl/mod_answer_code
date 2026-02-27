# src/services/semantic_repo_service.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple
import os
import re

from config import Config


@dataclass(frozen=True)
class RepoPick:
    repos: List[str]
    category: str
    why: str


class SemanticRepoService:
    """
    Router semántico (simple y rápido) para elegir en qué repos buscar.

    - Input: question (texto libre)
    - Output: lista de repos en formato "PROJECT/REPO"
    - Estrategia:
        1) Detecta categoría por keywords
        2) Usa repos definidos en env por categoría si existen (AZURE_REPOS_<CAT>)
        3) Si no hay repos por categoría, cae a AZURE_CORE_REPOS
        4) Siempre añade core al final (opcional) para que haya contexto base
    """

    # Orden de prioridad de categorías (si hay empate)
    CATEGORY_PRIORITY = [
        "payments",
        "auth",
        "file",
        "email",
        "ui",
        "routing",
        "database",
        "general",
    ]

    # Palabras clave por categoría (ajusta cuando quieras)
    CATEGORY_KEYWORDS: Dict[str, List[str]] = {
        "payments": [
            "pago", "pagos", "payment", "checkout", "pasarela", "stripe", "paypal",
            "factura", "invoice", "billing", "cobro", "cobrar", "transaccion", "transacción",
            "recaudo", "subscription", "suscripcion", "suscripción", "orden de pago", "order",
        ],
        "auth": [
            "login", "auth", "autenticar", "autenticacion", "autenticación", "token",
            "sesion", "sesión", "jwt", "oauth", "permiso", "rol", "usuario", "islogged",
        ],
        "file": [
            "descargar", "download", "archivo", "file", "pdf", "excel", "csv", "zip",
            "adjunto", "attachment", "stream", "content-disposition", "readfile", "visor",
        ],
        "email": [
            "correo", "email", "mail", "smtp", "notificar", "notificacion", "notificación",
            "newsletter", "phpmailer", "mailer",
        ],
        "ui": [
            "menu", "menú", "navbar", "sidebar", "breadcrumb", "miga", "layout",
            "template", "view", "css", "js", "front", "boton", "botón", "header", "footer",
        ],
        "routing": [
            "ruta", "route", "router", "endpoint", "controlador", "controller", "handler",
            "request", "response",
        ],
        "database": [
            "bd", "database", "sql", "query", "insert", "update", "select", "repository",
            "dao", "model", "entity", "persistir", "guardar",
        ],
        "general": [],
    }

    # Regex para detectar pistas de microservicio por texto
    # (ej: "ms_pagos", "mod_pagos", "payments-service", etc.)
    SERVICE_HINT_RE = re.compile(r"\b(ms|mod)[\-_]?[a-z0-9_]+\b", re.IGNORECASE)

    def pick_repos(self, question: str) -> List[str]:
        pick = self.pick_repos_with_debug(question)
        return pick.repos

    def pick_repos_with_debug(self, question: str) -> RepoPick:
        q = (question or "").strip()
        ql = q.lower()

        # 1) puntuar categorías
        scores: Dict[str, int] = {c: 0 for c in self.CATEGORY_KEYWORDS.keys()}

        for cat, kws in self.CATEGORY_KEYWORDS.items():
            for kw in kws:
                if kw in ql:
                    # si coincide literal, suma fuerte
                    scores[cat] += 10

    
        if self.SERVICE_HINT_RE.search(ql):
            scores["routing"] += 2
            scores["database"] += 1

        # 3) elegir mejor categoría (por score y prioridad)
        best_cat = self._choose_best_category(scores)

        
        cat_repos = self._read_repos_env_for_category(best_cat)

        # 5) fallback a core si no hay
        if not cat_repos:
            cat_repos = list(Config.AZURE_CORE_REPOS)

        # 6) opcional: siempre incluir core al final como red de seguridad
        repos = self._merge_with_core(cat_repos)

        why = f"category={best_cat}, scores={self._compact_scores(scores)}"
        return RepoPick(repos=repos, category=best_cat, why=why)

    # ---------------- internals ----------------

    def _choose_best_category(self, scores: Dict[str, int]) -> str:
        # ordena por score desc y por prioridad
        # si todo es 0 -> general
        if all(v <= 0 for v in scores.values()):
            return "general"

        # max score
        max_score = max(scores.values())
        tied = [c for c, s in scores.items() if s == max_score]

        if len(tied) == 1:
            return tied[0]

        # desempate por prioridad fija
        for p in self.CATEGORY_PRIORITY:
            if p in tied:
                return p

        return tied[0]

    def _read_repos_env_for_category(self, category: str) -> List[str]:
        env_key = f"AZURE_REPOS_{category.upper()}"
        raw = os.getenv(env_key, "").strip()
        repos = [x.strip() for x in raw.split(",") if x.strip()]
        # deben estar en formato PROJECT/REPO para que AzureDevOpsService funcione
        repos = [r for r in repos if "/" in r]
        return repos

    def _merge_with_core(self, repos: List[str]) -> List[str]:
        # evita duplicados manteniendo orden
        out: List[str] = []
        seen = set()

        for r in repos:
            if r not in seen:
                out.append(r)
                seen.add(r)

        for r in Config.AZURE_CORE_REPOS:
            if r not in seen:
                out.append(r)
                seen.add(r)

        return out[: max(1, Config.MAX_REPOS)]

    def _compact_scores(self, scores: Dict[str, int]) -> str:
        # devuelve algo tipo "payments:20,auth:10,file:0"
        parts = []
        for k in self.CATEGORY_PRIORITY:
            if k in scores:
                parts.append(f"{k}:{scores[k]}")
        # incluye otras si existen
        for k, v in scores.items():
            if k not in self.CATEGORY_PRIORITY:
                parts.append(f"{k}:{v}")
        return ",".join(parts)
