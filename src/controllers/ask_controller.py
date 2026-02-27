import json
import uuid
import io
from flask import Blueprint, request, jsonify, Response, send_file

from src.services.code_context_service import CodeContextService
from src.services.semantic_repo_service import SemanticRepoService
from src.services.prompt_service import PromptService
from src.services.gemini_service import GeminiService

ask_bp = Blueprint("ask", __name__)

def _build_multipart_response(payload: dict, code_text: str, filename: str = "codigo_extraido.txt") -> Response:
    boundary = "----nexura_" + uuid.uuid4().hex

    json_bytes = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    code_bytes = (code_text or "").encode("utf-8")

    parts = []
    parts.append(f"--{boundary}\r\n".encode("utf-8"))
    parts.append(b"Content-Type: application/json; charset=utf-8\r\n")
    parts.append(b"Content-Disposition: inline\r\n\r\n")
    parts.append(json_bytes)
    parts.append(b"\r\n")

    parts.append(f"--{boundary}\r\n".encode("utf-8"))
    parts.append(b"Content-Type: text/plain; charset=utf-8\r\n")
    parts.append(f'Content-Disposition: attachment; filename="{filename}"\r\n\r\n'.encode("utf-8"))
    parts.append(code_bytes)
    parts.append(b"\r\n")

    parts.append(f"--{boundary}--\r\n".encode("utf-8"))

    body = b"".join(parts)
    return Response(
        body,
        status=200,
        mimetype=f"multipart/mixed; boundary={boundary}",
        headers={"Cache-Control": "no-store"},
    )

def _context_to_code_txt(ctx: dict) -> str:
    header = []
    repos_used = ctx.get("repos_used") or []
    matched_files = ctx.get("matched_files") or []
    topic_tokens = ctx.get("topic_tokens") or []
    intent_keys = ctx.get("intent_keys") or []

    header.append("NEXURA CODE EXTRACT")
    header.append("=" * 80)

    if repos_used:
        header.append("REPOS:")
        for r in repos_used:
            header.append(f" - {r}")

    if topic_tokens:
        header.append("\nTOPIC TOKENS (path hints): " + ", ".join(topic_tokens[:30]))
    if intent_keys:
        header.append("INTENT KEYS: " + ", ".join(intent_keys[:30]))

    if matched_files:
        header.append("\nMATCHED FILES (selected):")
        for f in matched_files[:30]:
            header.append(f" - {f}")

    header.append("\n" + "=" * 80)
    header.append("SNIPPETS")
    header.append("=" * 80 + "\n")

    body = (ctx.get("context") or "").strip()
    return "\n".join(header) + "\n" + body + "\n"

@ask_bp.route("/ask_multipart", methods=["POST"], endpoint="ask_multipart")
def ask_multipart():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    if not question:
        return jsonify({"ok": False, "code": "BAD_REQUEST", "error": "Campo 'question' o pregunta requerida"}), 400

    # Router semántico: selecciona repos objetivo
    target_repos = SemanticRepoService().pick_repos(question)

    # Contexto SOLO de esos repos
    ctx = CodeContextService().build_context(question, target_repos=target_repos)

    # Llamada al LLM
    prompt = PromptService().build_prompt(question, ctx)
    llm = GeminiService().answer(prompt)
    parsed = llm.get("parsed") if isinstance(llm.get("parsed"), dict) else None

    if parsed and isinstance(parsed.get("analysis"), dict):
        analysis_payload = parsed["analysis"]
    else:
        analysis_payload = {
            "answer": llm.get("answer", ""),
            "key_points": [],
            "references": [],
            "debug": {
                "repos_used": ctx.get("repos_used", []),
                "matched_files_count": len(ctx.get("matched_files") or []),
            }
        }

    code_text = ""
    if parsed and isinstance(parsed.get("code_text"), str):
        code_text = parsed["code_text"].strip()

    if not code_text:
        code_text = _context_to_code_txt(ctx)

    return _build_multipart_response(analysis_payload, code_text, filename="codigo_extraido.txt")

@ask_bp.route("/code", methods=["POST"], endpoint="ask_code_only")
def ask_code_only():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    if not question:
        return jsonify({"ok": False, "code": "BAD_REQUEST", "error": "Campo 'question' es requerido"}), 400

    target_repos = SemanticRepoService().pick_repos(question)
    ctx = CodeContextService().build_context(question, target_repos=target_repos)

    code_text = _context_to_code_txt(ctx)
    buf = io.BytesIO(code_text.encode("utf-8"))
    buf.seek(0)

    return send_file(
        buf,
        mimetype="text/plain",
        as_attachment=True,
        download_name="codigo_extraido.txt",
    )
