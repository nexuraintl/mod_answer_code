from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional, Set
import re
import time

from config import Config
from src.models.errors import AppError
from src.services.azure_devops_service import AzureDevOpsService


@dataclass
class Snippet:
    project: str
    repo: str
    path: str
    text: str
    why: str
    lines: str
    relevance_score: int = 0


class CodeContextService:
    """
    Construye contexto de código PRECISO y CONCISO desde repositorios.

    Objetivos:
    - responder rápido
    - minimizar falsos positivos (ruido: translations, docs, build scripts)
    - soportar preguntas explicativas (traer bloques completos cuando conviene)
    - soportar repos "objetivo" (override) para router semántico
    """

    # defaults (modo rápido)
    MAX_SNIPPET_LINES = 25
    IDEAL_SNIPPET_LINES = 15
    MIN_SNIPPET_LINES = 7
    MAX_SNIPPETS_PER_FILE = 2
    MIN_RELEVANCE_SCORE = 2

    # cache simple en memoria (reduce latencia)
    _tree_cache: Dict[str, Tuple[float, List[dict]]] = {}
    _file_cache: Dict[str, Tuple[float, str]] = {}
    TREE_TTL_SEC = 300
    FILE_TTL_SEC = 300

    # patrones de "ruido" (no siempre malos, pero suelen confundir respuestas)
    NOISE_PATH_SUBSTRINGS = [
        "/language/", "/lang/", "/translations/", "/i18n/",
        "/node_modules/", "/dist/", "/build/",
        "/tests/", "/test/", "/mock/", "/fixtures/",
    ]

    # algunos nombres específicos que suelen ser build tooling
    NOISE_FILES = [
        "gulpfile.js", "webpack.config", "rollup.config", "vite.config"
    ]

    def __init__(self):
        self.azure = AzureDevOpsService()

    # ===================== PUBLIC =====================

    def build_context(self, question: str, target_repos: Optional[List[str]] = None) -> Dict[str, object]:
        """
        Construye contexto para una pregunta.

        target_repos: si se pasa, se usan esos repos (ideal para router semántico).
        lista de strings en formato: ["PROJECT/REPO", ...]
        """
        repos_base = target_repos or Config.AZURE_CORE_REPOS
        repos = repos_base[: Config.MAX_REPOS]
        if not repos:
            raise AppError("AZURE_CORE_REPOS vacío", "CONFIG_ERROR", 500)

        intent = self._analyze_intent(question)
        if not intent["keywords"]:
            raise AppError(
                "No se pudieron identificar términos técnicos específicos en la pregunta.",
                "NO_CONTEXT",
                404,
            )

        is_expl = self._is_explanatory_question(question)
        explicit_path = self._extract_explicit_path(question)

        # si el usuario menciona un archivo explícito, lo priorizamos como keyword (ayuda ranking)
        if explicit_path and explicit_path not in intent["keywords"]:
            intent["keywords"] = [explicit_path] + intent["keywords"]
            intent["keywords"] = intent["keywords"][:30]

        # modo explicativo: permite bloques más grandes
        max_snippet_lines = 120 if is_expl else self.MAX_SNIPPET_LINES
        ideal_window = 60 if is_expl else self.IDEAL_SNIPPET_LINES
        max_snips_per_file = 4 if is_expl else self.MAX_SNIPPETS_PER_FILE

        all_snips: List[Snippet] = []

        for pr in repos:
            project, repo = self._split_project_repo(pr)

            items = self._list_items_cached(project, repo)
            paths = self._extract_allowed_paths(items)
            if not paths:
                continue

            ranked_paths = self._rank_paths_by_relevance(
                paths=paths,
                intent=intent,
                explicit_path=explicit_path,
            )

            # menos paths = más rápido (sube en explicativas un poco)
            top_paths_limit = 20 if is_expl else 12
            all_snips += self._extract_relevant_snippets(
                project=project,
                repo=repo,
                ranked_paths=ranked_paths[:top_paths_limit],
                intent=intent,
                max_snippet_lines=max_snippet_lines,
                ideal_window=ideal_window,
                max_snips_per_file=max_snips_per_file,
                is_expl=is_expl,
            )

            if len(all_snips) >= Config.MAX_FILES * 4:
                break

        final_snips = self._deduplicate_and_rank(all_snips)

        # --- EXTRA: en modo explicativo, intenta agregar "usos" (call sites) ---
        # Esto ayuda a que el modelo pueda decir:
        # 1) qué es (definición)
        # 2) dónde se usa / dónde tocar (uso en controllers/servicios/etc.)
        if is_expl and final_snips:
            extra_keywords: List[str] = []
            for s in final_snips[:2]:
                extra_keywords += self._extract_symbol_hints_from_text(s.text)

            extra_keywords = [k for k in extra_keywords if k and k not in intent["keywords"]]
            if extra_keywords:
                intent_uses = {
                    "keywords": (intent["keywords"] + extra_keywords)[:30],
                    "categories": intent.get("categories") or [],
                }

                more_snips: List[Snippet] = []
                for pr in repos:
                    project, repo = self._split_project_repo(pr)
                    items = self._list_items_cached(project, repo)
                    paths = self._extract_allowed_paths(items)
                    if not paths:
                        continue

                    ranked_paths = self._rank_paths_by_relevance(paths, intent_uses, explicit_path=None)
                    more_snips += self._extract_relevant_snippets(
                        project=project,
                        repo=repo,
                        ranked_paths=ranked_paths[:10],  # corto para performance
                        intent=intent_uses,
                        max_snippet_lines=80,
                        ideal_window=40,
                        max_snips_per_file=1,
                        is_expl=True,
                    )

                final_snips = self._deduplicate_and_rank(final_snips + more_snips)

        final_snips = final_snips[: Config.MAX_FILES]

        if not final_snips:
            raise AppError(
                "Por favor especifique mejor su pregunta o revise que el repositorio tenga código relevante. No se encontraron archivos relacionados con la pregunta.",
                "NO_CONTEXT",
                404,
            )

        context = self._build_context_string(final_snips)
        analysis = self._build_analysis(final_snips, intent, question, is_expl, explicit_path)

        matched_files = [f"{s.project}/{s.repo}{s.path}" for s in final_snips]

        return {
            "context": context,
            "analysis": analysis,
            "snippets_count": len(final_snips),
            "keywords_matched": intent["keywords"][:10],
            "repos_used": repos,
            "matched_files": matched_files,
            # para tu TXT (sirven como “hints”)
            "topic_tokens": intent.get("categories") or [],
            "intent_keys": intent.get("keywords") or [],
        }

    # ===================== INTENT =====================

    def _is_explanatory_question(self, question: str) -> bool:
        q = (question or "").lower()
        triggers = [
            "como funciona", "cómo funciona", "explica", "explícame",
            "flujo", "proceso", "paso a paso", "cómo se", "como se",
            "que hace", "qué hace", "como genera", "cómo genera",
            "dentro de", "en el archivo", "en la clase", "en la función",
            "por qué", "porque", "de qué depende",
        ]
        return any(t in q for t in triggers)

    def _extract_explicit_path(self, question: str) -> Optional[str]:
        q = question or ""
        m = re.search(r"([A-Za-z0-9_\-\/\.]+\.(php|py|js|ts|java|html|css|sql|go|cs|rb))", q)
        return m.group(1) if m else None

    def _analyze_intent(self, question: str) -> Dict[str, object]:
        q = (question or "").lower()

        # keywords base
        base_keywords: List[str] = []
        for word in re.findall(r"\b[a-zA-Z_]{3,}\b", q):
            if word not in [
                "como", "que", "donde", "cuando", "cual", "hace", "esta", "son", "hay",
                "para", "con", "del", "las", "los", "una", "uno", "por", "sobre"
            ]:
                base_keywords.append(word)

        # categorías (solo para boosts suaves)
        categories: List[str] = []
        if any(x in q for x in ["login", "autenticar", "token", "sesion", "sesión", "permiso", "rol", "usuario", "logueado"]):
            categories.append("auth")
        if any(x in q for x in ["descargar", "download", "archivo", "file", "pdf", "visor", "visualizar", "adjunto"]):
            categories.append("file")
        if any(x in q for x in ["menu", "menú", "navbar", "breadcrumb", "miga", "css", "js", "layout", "botones"]):
            categories.append("ui")
        if any(x in q for x in ["ruta", "route", "endpoint", "controlador", "controller"]):
            categories.append("routing")
        if any(x in q for x in ["composer", "autoload", "vendor", "namespace", "use "]):
            categories.append("composer")
        if any(x in q for x in ["pago", "pagos", "payment", "checkout", "pasarela", "factura", "invoice"]):
            categories.append("payments")
        if any(x in q for x in ["notificar", "notificación", "correo", "email", "mail", "smtp", "newsletter"]):
            categories.append("email")

        # términos técnicos expandibles (generales)
        tech_terms = set()
        if "auth" in categories:
            tech_terms.update(["auth", "login", "token", "session", "sesion", "middleware", "guard", "islogged"])
        if "file" in categories:
            tech_terms.update(["download", "descargar", "readfile", "content-disposition", "attachment", "pdf", "visorpdf"])
        if "ui" in categories:
            tech_terms.update(["layout", "header", "footer", "menu", "navbar", "breadcrumb", "miga", "genurl", "template", "view"])
        if "routing" in categories:
            tech_terms.update(["route", "router", "controller", "endpoint", "request", "response"])
        if "composer" in categories:
            tech_terms.update(["composer", "autoload", "vendor", "namespace", "use", "require"])
        if "payments" in categories:
            tech_terms.update(["pago", "pagos", "payment", "checkout", "invoice", "factura", "pasarela"])
        if "email" in categories:
            tech_terms.update(["mail", "email", "smtp", "phpmailer", "notify", "newsletter"])

        keywords: List[str] = []
        seen = set()
        for w in base_keywords:
            if w not in seen:
                keywords.append(w)
                seen.add(w)
        for w in tech_terms:
            if w not in seen:
                keywords.append(w)
                seen.add(w)

        return {
            "keywords": keywords[:30],
            "categories": categories,
        }

    def _extract_symbol_hints_from_text(self, text: str) -> List[str]:
        """
        Extrae pistas de símbolos para buscar usos:
        - PHP: thumbnail::createThumb(
        - Python: def foo(
        - Clases: class Foo
        """
        hints: List[str] = []
        if not text:
            return hints

        # funciones PHP
        for m in re.finditer(r"\bfunction\s+([A-Za-z_]\w*)\s*\(", text):
            hints.append(m.group(1) + "(")

        # clases (general)
        for m in re.finditer(r"\bclass\s+([A-Za-z_]\w*)\b", text):
            cls = m.group(1)
            hints.append(cls)
            hints.append(cls + "::")

        # funciones Python
        for m in re.finditer(r"^\s*def\s+([A-Za-z_]\w*)\s*\(", text, flags=re.MULTILINE):
            hints.append(m.group(1) + "(")

        out: List[str] = []
        seen = set()
        for h in hints:
            if h not in seen and len(h) >= 3:
                out.append(h)
                seen.add(h)
        return out[:6]

    # ===================== AZURE CACHES =====================

    def _list_items_cached(self, project: str, repo: str) -> List[dict]:
        key = f"{project}/{repo}"
        now = time.time()
        if key in self._tree_cache:
            ts, items = self._tree_cache[key]
            if now - ts < self.TREE_TTL_SEC:
                return items

        tree = self.azure.list_items(project, repo)
        items = tree.get("value") or []
        self._tree_cache[key] = (now, items)
        return items

    def _get_file_cached(self, project: str, repo: str, path: str) -> str:
        key = f"{project}/{repo}:{path}"
        now = time.time()
        if key in self._file_cache:
            ts, content = self._file_cache[key]
            if now - ts < self.FILE_TTL_SEC:
                return content

        content, _meta = self.azure.get_file_content(project, repo, path)
        content = content or ""
        self._file_cache[key] = (now, content)
        return content

    # ===================== PATH RANKING =====================

    def _rank_paths_by_relevance(
        self,
        paths: List[str],
        intent: Dict[str, object],
        explicit_path: Optional[str],
    ) -> List[Tuple[int, str]]:
        keywords = (intent.get("keywords") or [])[:20]
        cats = intent.get("categories") or []

        scored: List[Tuple[int, str]] = []
        for path in paths:
            lp = path.lower()
            score = 0

            if explicit_path and explicit_path.lower() in lp:
                score += 200

            # penalizaciones suaves por ruido (pero no rompas email/ui por lang)
            if any(s in lp for s in self.NOISE_PATH_SUBSTRINGS):
                if not any(c in cats for c in ["email", "ui"]):
                    score -= 15

            if any(n in lp for n in self.NOISE_FILES):
                score -= 20

            if ("composer" not in cats) and any(x in lp for x in ["/vendor/", "/composer/"]):
                score -= 10

            # keywords en path (lo más importante)
            for i, kw in enumerate(keywords):
                if not isinstance(kw, str):
                    continue
                k = kw.lower().strip()
                if k and k in lp:
                    score += max(12 - i, 1) * 3

            # boosts suaves por categoría
            if "ui" in cats and any(x in lp for x in ["layout", "header", "footer", "menu", "navbar", "view", "template"]):
                score += 12
            if "file" in cats and any(x in lp for x in ["download", "descargar", "visor", "pdf", "document", "archivo"]):
                score += 12
            if "auth" in cats and any(x in lp for x in ["auth", "login", "session", "sesion", "usuario"]):
                score += 10
            if "routing" in cats and any(x in lp for x in ["route", "router", "controller", "endpoint"]):
                score += 8
            if "payments" in cats and any(x in lp for x in ["pago", "payment", "checkout", "invoice", "factura"]):
                score += 10
            if "email" in cats and any(x in lp for x in ["mail", "email", "smtp", "phpmailer"]):
                score += 8

            if score > 0:
                scored.append((score, path))

        scored.sort(reverse=True, key=lambda x: x[0])
        return scored

    # ===================== SNIPPET EXTRACTION =====================

    def _extract_relevant_snippets(
        self,
        project: str,
        repo: str,
        ranked_paths: List[Tuple[int, str]],
        intent: Dict[str, object],
        max_snippet_lines: int,
        ideal_window: int,
        max_snips_per_file: int,
        is_expl: bool,
    ) -> List[Snippet]:
        snippets: List[Snippet] = []
        keywords = (intent.get("keywords") or [])[:25]

        regex_patterns = []
        for kw in keywords:
            if isinstance(kw, str) and len(kw) >= 3:
                regex_patterns.append(re.escape(kw))

        if not regex_patterns:
            return []

        regex = re.compile("|".join(regex_patterns), re.IGNORECASE)

        for path_score, path in ranked_paths:
            try:
                content = self._get_file_cached(project, repo, path)
            except Exception:
                continue
            if not content:
                continue

            content = content[: Config.MAX_FILE_BYTES]
            lines = content.splitlines()

            # filtro ionCube
            head = "\n".join(lines[:8]).lower()
            if "ioncube loader" in head and "<?php //004fb" in head:
                continue

            match_lines = []
            for i, line in enumerate(lines):
                if regex.search(line):
                    match_lines.append(i)
                    if len(match_lines) >= 15:
                        break
            if not match_lines:
                continue

            extracted = self._extract_snippets_from_matches(
                lines=lines,
                match_indices=match_lines,
                ideal_window=ideal_window,
                max_snippet_lines=max_snippet_lines,
                max_snips=max_snips_per_file,
                is_expl=is_expl,
            )

            for snippet_text, line_range, relevance in extracted:
                snippets.append(
                    Snippet(
                        project=project,
                        repo=repo,
                        path=path,
                        text=snippet_text,
                        why=self._generate_why(path, intent.get("categories") or []),
                        lines=line_range,
                        relevance_score=path_score + relevance,
                    )
                )

        return snippets

    def _extract_snippets_from_matches(
        self,
        lines: List[str],
        match_indices: List[int],
        ideal_window: int,
        max_snippet_lines: int,
        max_snips: int,
        is_expl: bool,
    ) -> List[Tuple[str, str, int]]:
        snippets: List[Tuple[str, str, int]] = []
        used_ranges: Set[Tuple[int, int]] = set()

        for idx in match_indices:
            block = None
            if is_expl:
                block = self._extract_smart_block(lines, idx, max_lines=max_snippet_lines)

            if block:
                text, start, end, rel = block
            else:
                start, end, text = self._create_focused_window(lines, idx, ideal_window)
                rel = 6

            if self._has_significant_overlap(start, end, used_ranges):
                continue
            used_ranges.add((start, end))

            low = text.lower()
            if any(x in low for x in ["function", "class ", "def ", "public function", "private function", "return "]):
                rel += 6
            if any(x in low for x in ["header(", "readfile(", "session", "route", "controller", "sql", "select "]):
                rel += 4

            snippets.append((text, f"{start+1}-{end}", rel))
            if len(snippets) >= max_snips:
                break

        return snippets

    def _extract_smart_block(
        self,
        lines: List[str],
        match_idx: int,
        max_lines: int = 120,
    ) -> Optional[Tuple[str, int, int, int]]:
        start = self._find_block_start(lines, match_idx, max_lookback=60)
        if start is None:
            return None

        start_line = lines[start].strip()
        is_python = bool(re.match(r"^\s*def\s+\w+", start_line))
        is_php_func = bool(re.match(r"^\s*(public|private|protected)?\s*function\s+\w+", start_line))
        is_php_class = bool(re.match(r"^\s*class\s+\w+", start_line))
        has_brace = "{" in start_line or is_php_func or is_php_class

        if is_python:
            end = self._find_python_block_end(lines, start, max_lines=max_lines)
        elif has_brace:
            end = self._find_brace_block_end(lines, start, max_lines=max_lines)
        else:
            end = min(len(lines), start + min(max_lines, 80))

        if end <= start:
            return None

        text = "\n".join(lines[start:end]).strip()
        return (text, start, end, 12)

    def _find_block_start(self, lines: List[str], idx: int, max_lookback: int = 60) -> Optional[int]:
        patterns = [
            r"^\s*def\s+\w+\s*\(",
            r"^\s*(public|private|protected)?\s*function\s+\w+\s*\(",
            r"^\s*class\s+\w+",
        ]
        regex = re.compile("|".join(patterns))
        start_search = max(0, idx - max_lookback)
        for i in range(idx, start_search - 1, -1):
            if regex.match(lines[i]):
                return i
        return None

    def _find_python_block_end(self, lines: List[str], start: int, max_lines: int = 120) -> int:
        base_indent = len(lines[start]) - len(lines[start].lstrip())
        for i in range(start + 1, min(len(lines), start + max_lines)):
            line = lines[i]
            if not line.strip():
                continue
            indent = len(line) - len(line.lstrip())
            if indent <= base_indent and not line.strip().startswith(("#", "@")):
                return i
        return min(len(lines), start + max_lines)

    def _find_brace_block_end(self, lines: List[str], start: int, max_lines: int = 120) -> int:
        brace = 0
        found = False
        for i in range(start, min(len(lines), start + max_lines)):
            line = lines[i]
            o = line.count("{")
            c = line.count("}")
            if o:
                found = True
            brace += o - c
            if found and brace == 0 and i > start:
                return i + 1
        return min(len(lines), start + max_lines)

    def _create_focused_window(self, lines: List[str], center_idx: int, window_size: int) -> Tuple[int, int, str]:
        half = max(1, window_size // 2)
        start = max(0, center_idx - half)
        end = min(len(lines), start + window_size)
        if end == len(lines) and end - start < window_size:
            start = max(0, end - window_size)
        return start, end, "\n".join(lines[start:end]).strip()

    def _has_significant_overlap(self, start: int, end: int, used_ranges: Set[Tuple[int, int]]) -> bool:
        new_range = set(range(start, end))
        new_size = len(new_range) or 1
        for a, b in used_ranges:
            old_range = set(range(a, b))
            overlap = len(new_range & old_range)
            if overlap / new_size > 0.3:
                return True
        return False

    # ===================== DEDUP & OUTPUT =====================

    def _deduplicate_and_rank(self, snippets: List[Snippet]) -> List[Snippet]:
        if not snippets:
            return []
        seen: Set[str] = set()
        out: List[Snippet] = []
        for s in snippets:
            fp = self._fingerprint(s.path, s.lines, s.text)
            if fp not in seen:
                seen.add(fp)
                out.append(s)
        out.sort(key=lambda x: x.relevance_score, reverse=True)
        return [s for s in out if s.relevance_score >= self.MIN_RELEVANCE_SCORE]

    def _fingerprint(self, path: str, lines: str, text: str) -> str:
        norm = re.sub(r"\s+", " ", (text or "").lower().strip())
        return f"{path}|{lines}|{norm[:180]}"

    def _generate_why(self, path: str, categories: List[str]) -> str:
        if categories:
            return f"Match por keywords + categoría {categories[0]} (boost suave)"
        return "Match por keywords"

    def _build_context_string(self, snippets: List[Snippet]) -> str:
        blocks = []
        total_chars = 0
        for snip in snippets:
            full_path = f"{snip.project}/{snip.repo}{snip.path}"
            block = (
                f"FILE: {full_path}\n"
                f"LINES: {snip.lines}\n"
                f"RELEVANCE: {snip.relevance_score}\n"
                f"WHY: {snip.why}\n"
                f"{'─' * 60}\n"
                f"{snip.text}\n"
            )
            if total_chars + len(block) > Config.MAX_CONTEXT_CHARS:
                break
            blocks.append(block)
            total_chars += len(block)
        return "\n\n".join(blocks)

    def _build_analysis(
        self,
        snippets: List[Snippet],
        intent: Dict[str, object],
        question: str,
        is_expl: bool,
        explicit_path: Optional[str],
    ) -> str:
        cats = intent.get("categories") or []
        kws = intent.get("keywords") or []
        lines = [
            "ANÁLISIS DEL CONTEXTO EXTRAÍDO",
            "=" * 60,
            f"Pregunta: {question}",
            f"Modo: {'EXPLICATIVO' if is_expl else 'RÁPIDO'}",
            f"Archivo explícito: {explicit_path or 'N/A'}",
            f"Snippets: {len(snippets)}",
            f"Categorías: {', '.join(cats) if cats else 'General'}",
            f"Keywords: {', '.join(kws[:10])}",
        ]
        return "\n".join(lines)

    # ===================== UTILS =====================

    def _split_project_repo(self, pr: str) -> Tuple[str, str]:
        if "/" not in pr:
            raise AppError(
                f"AZURE_CORE_REPOS inválido: '{pr}'. Debe ser PROJECT/REPO",
                "CONFIG_ERROR",
                500,
            )
        project, repo = pr.split("/", 1)
        return project.strip(), repo.strip()

    def _extract_allowed_paths(self, items: list) -> List[str]:
        allowed: List[str] = []
        for item in items:
            path = item.get("path")
            if not isinstance(path, str):
                continue
            if item.get("isFolder", False):
                continue
            if path.lower().endswith(Config.ALLOWED_EXT):
                allowed.append(path)
        return allowed
