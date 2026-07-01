import re
from datetime import date, datetime, timezone

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.repositories.chunk_repository import ChunkRepository
from app.repositories.experience_repository import ExperienceRepository
from app.repositories.question_repository import QuestionRepository
from app.schemas.answer_update import ExperienceAnswerUpdateDecision, ExperienceFieldUpdate
from app.services.answer_interpretation_service import AnswerInterpretationService
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.utils.scoring import contains_metric


class QuestionAnswerService:
    def __init__(self, db: Session, interpreter: AnswerInterpretationService | None = None):
        self.db = db
        self.questions = QuestionRepository(db)
        self.experiences = ExperienceRepository(db)
        self.chunks = ChunkRepository(db)
        self.chunker = ChunkingService()
        self.embeddings = EmbeddingService()
        self.interpreter = interpreter or AnswerInterpretationService()

    def answer(self, question_id: str, answer: str) -> tuple[str, str, float]:
        question = self.questions.get(question_id)
        if question is None:
            raise AppError(404, "question_not_found", "Question not found.")
        experience = self.experiences.get(question.experience_id)
        if experience is None:
            raise AppError(404, "experience_not_found", "Experience not found.")

        question.answer = answer
        question.status = "answered"
        question.answered_at = datetime.now(timezone.utc)

        decision = self.interpreter.interpret(experience, question, answer)
        if not decision.updates:
            decision = ExperienceAnswerUpdateDecision(
                updates=[ExperienceFieldUpdate(field="action", value=answer, mode="append")]
            )
        self._apply_updates(experience, decision)
        self._refresh_flags(experience)

        current_score = float(experience.completeness_score)
        bonus = 12 if contains_metric(answer) else 8
        experience.completeness_score = min(100, current_score + bonus)
        if experience.completeness_score >= 80:
            experience.status = "confirmed"
        elif experience.completeness_score >= 50:
            experience.status = "needs_review"

        source_document_id = experience.sources[0].source_document_id if experience.sources else None
        self.chunks.delete_by_experience(experience.id)
        chunks = self.chunker.build_chunks(experience, source_document_id)
        for chunk in chunks:
            from uuid import uuid4

            chunk.id = str(uuid4())
            chunk.embedding = self.embeddings.embed(chunk.chunk_text)
        self.chunks.create_many(chunks)
        self.db.commit()
        return question.id, experience.id, float(experience.completeness_score)

    @staticmethod
    def _append(current: str | None, answer: str) -> str:
        return f"{current} {answer}".strip() if current else answer

    def _apply_updates(self, experience, decision: ExperienceAnswerUpdateDecision) -> None:
        for update in decision.updates:
            value = self._coerce_value(update.field, update.value)
            if update.field in {"skills", "competencies", "keywords"}:
                current = getattr(experience, update.field) or []
                values = value if isinstance(value, list) else [value]
                if update.mode == "append":
                    setattr(experience, update.field, self._merge_unique(current, values))
                else:
                    setattr(experience, update.field, [item for item in values if item])
            elif update.mode == "append" and isinstance(value, str):
                current = getattr(experience, update.field)
                setattr(experience, update.field, self._append(current, value))
            else:
                setattr(experience, update.field, value)

    @staticmethod
    def _coerce_value(field: str, value):
        if field in {"start_date", "end_date"}:
            if value in {None, ""}:
                return None
            if isinstance(value, date):
                return value
            text = str(value)
            try:
                return date.fromisoformat(text)
            except ValueError:
                parsed = _extract_dates(text)
                if parsed:
                    return parsed[0]
                raise
        return value

    @staticmethod
    def _refresh_flags(experience) -> None:
        experience.has_metric = contains_metric(experience.result) or contains_metric(experience.action)
        experience.has_role = bool(experience.role)
        experience.has_result = bool(experience.result)
        experience.has_learning = bool(experience.learned)

    @staticmethod
    def _merge_unique(current: list, values: list) -> list:
        merged = list(current)
        for value in values:
            if value and value not in merged:
                merged.append(value)
        return merged


def _extract_dates(text: str) -> list[date]:
    dates = []
    seen = set()
    patterns = [
        re.compile(r"(?P<year>\d{4})[-./년]\s*(?P<month>\d{1,2})[-./월]\s*(?P<day>\d{1,2})"),
        re.compile(r"(?P<year>\d{4})\s*년\s*(?P<month>\d{1,2})\s*월\s*(?P<day>\d{1,2})\s*일"),
    ]
    for pattern in patterns:
        for match in pattern.finditer(text):
            parsed = date(int(match.group("year")), int(match.group("month")), int(match.group("day")))
            if parsed not in seen:
                dates.append(parsed)
                seen.add(parsed)
    return dates
