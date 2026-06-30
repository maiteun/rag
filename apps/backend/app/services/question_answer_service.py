from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.repositories.chunk_repository import ChunkRepository
from app.repositories.experience_repository import ExperienceRepository
from app.repositories.question_repository import QuestionRepository
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.utils.scoring import contains_metric


class QuestionAnswerService:
    def __init__(self, db: Session):
        self.db = db
        self.questions = QuestionRepository(db)
        self.experiences = ExperienceRepository(db)
        self.chunks = ChunkRepository(db)
        self.chunker = ChunkingService()
        self.embeddings = EmbeddingService()

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

        target = question.question_type or question.reason or ""
        if "metric" in target or "result" in target:
            experience.result = self._append(experience.result, answer)
            experience.has_result = True
            experience.has_metric = experience.has_metric or contains_metric(answer)
        elif "learning" in target:
            experience.learned = self._append(experience.learned, answer)
            experience.has_learning = True
        elif "role" in target:
            experience.role = self._append(experience.role, answer)
            experience.has_role = True
        else:
            experience.action = self._append(experience.action, answer)
            experience.has_metric = experience.has_metric or contains_metric(answer)

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

