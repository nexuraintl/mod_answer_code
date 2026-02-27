from dataclasses import dataclass
from src.models.errors import AppError

@dataclass
class AskRequest:
    question: str

    @staticmethod
    def from_dict(d: dict) -> "AskRequest":
        q = (d.get("question") or "").strip()
        if not q:
            raise AppError("Missing field: question", "VALIDATION_ERROR", 400)
        return AskRequest(question=q)
