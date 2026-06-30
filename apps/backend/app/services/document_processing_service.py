from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models.experience import Experience
from app.models.experience_source import ExperienceSource
from app.repositories.chunk_repository import ChunkRepository
from app.repositories.experience_repository import ExperienceRepository
from app.repositories.question_repository import QuestionRepository
from app.repositories.source_document_repository import SourceDocumentRepository
from app.schemas.experience import ExperienceProcessingSummary, QuestionSummary
from app.schemas.llm import ExperienceDraft
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.experience_extraction_service import ExperienceExtractionService
from app.services.question_service import QuestionService
from app.services.text_cleaning_service import TextCleaningService
from app.utils.scoring import calculate_completeness, contains_metric, status_for_score
from app.utils.text import contains_any


class DocumentProcessingService:
    def __init__(
        self,
        db: Session,
        cleaner: TextCleaningService | None = None,
        extractor: ExperienceExtractionService | None = None,
        chunker: ChunkingService | None = None,
        embeddings: EmbeddingService | None = None,
        questions: QuestionService | None = None,
    ):
        self.db = db
        self.documents = SourceDocumentRepository(db)
        self.experiences = ExperienceRepository(db)
        self.chunks = ChunkRepository(db)
        self.question_repo = QuestionRepository(db)
        self.cleaner = cleaner or TextCleaningService()
        self.extractor = extractor or ExperienceExtractionService()
        self.chunker = chunker or ChunkingService()
        self.embeddings = embeddings or EmbeddingService()
        self.questions = questions or QuestionService()

    def process(self, document_id: str) -> tuple[str, int, int]:
        document = self.documents.get(document_id)
        if document is None:
            raise AppError(404, "document_not_found", "Document not found.")
        if not document.raw_text:
            raise AppError(400, "missing_raw_text", "Document has no raw_text.")

        try:
            document.cleaned_text = self.cleaner.clean(document.raw_text)
            extraction = self.extractor.extract(document.cleaned_text)
            experience_count = 0
            question_count = 0

            for draft in extraction.experiences:
                experience = self._persist_experience(document.user_id, draft)
                self._persist_source(experience.id, document.id, draft)
                chunks = self.chunker.build_chunks(experience, document.id)
                for chunk in chunks:
                    chunk.id = str(uuid4())
                    try:
                        chunk.embedding = self.embeddings.embed(chunk.chunk_text)
                    except Exception as exc:  # embedding failure must not fail the document
                        chunk.embedding = None
                        chunk.chunk_metadata = {**(chunk.chunk_metadata or {}), "embedding_error": str(exc)}
                self.chunks.create_many(chunks)
                questions = self.questions.build_questions(document.user_id, experience.id, draft)
                for question in questions:
                    question.id = str(uuid4())
                self.question_repo.create_many(questions)
                experience_count += 1
                question_count += len(questions)

            document.status = "processed"
            self.db.commit()
            return document.status, experience_count, question_count
        except Exception as exc:
            document.status = "failed"
            document.doc_metadata = {**(document.doc_metadata or {}), "processing_error": str(exc)}
            self.db.commit()
            if isinstance(exc, AppError):
                raise
            raise AppError(500, "document_processing_failed", str(exc)) from exc

    def summaries_for_document(self, document_id: str) -> list[ExperienceProcessingSummary]:
        experiences = self.experiences.list_by_document(document_id)
        summaries = []
        for exp in experiences:
            questions = [
                QuestionSummary(
                    question_id=q.id,
                    question=q.question,
                    question_type=q.question_type,
                    priority=q.priority,
                    status=q.status,
                )
                for q in exp.questions
            ]
            summaries.append(
                ExperienceProcessingSummary(
                    experience_id=exp.id,
                    title=exp.title,
                    summary=exp.summary,
                    completeness_score=float(exp.completeness_score),
                    confidence_score=float(exp.confidence_score),
                    missing_fields=[q.question_type or "unknown" for q in exp.questions if q.status == "pending"],
                    questions=questions,
                )
            )
        return summaries

    def _persist_experience(self, user_id: str, draft: ExperienceDraft) -> Experience:
        completeness = calculate_completeness(draft)
        text = " ".join(
            part or ""
            for part in [
                draft.star.situation,
                draft.star.task,
                draft.star.action,
                draft.star.result,
                draft.star.learned,
            ]
        )
        experience = Experience(
            id=str(uuid4()),
            user_id=user_id,
            title=draft.title,
            summary=draft.summary,
            start_date=draft.period.start_date,
            end_date=draft.period.end_date,
            experience_type=draft.experience_type,
            organization=draft.organization,
            role=draft.role,
            situation=draft.star.situation,
            task=draft.star.task,
            action=draft.star.action,
            result=draft.star.result,
            learned=draft.star.learned,
            skills=draft.skills,
            competencies=draft.competencies,
            keywords=draft.keywords,
            has_metric=contains_metric(draft.star.result) or contains_metric(draft.star.action),
            has_role=bool(draft.role),
            has_result=bool(draft.star.result),
            has_conflict=contains_any(text, ["갈등", "의견 차이", "충돌", "조율", "conflict"]),
            has_learning=bool(draft.star.learned),
            completeness_score=completeness,
            confidence_score=draft.confidence_score,
            status=status_for_score(completeness),
        )
        return self.experiences.create(experience)

    def _persist_source(self, experience_id: str, document_id: str, draft: ExperienceDraft) -> None:
        evidence = draft.evidence[0] if draft.evidence else None
        self.experiences.create_source(
            ExperienceSource(
                id=str(uuid4()),
                experience_id=experience_id,
                source_document_id=document_id,
                source_span_start=evidence.span_start if evidence else None,
                source_span_end=evidence.span_end if evidence else None,
                source_excerpt=evidence.excerpt if evidence else None,
                extraction_confidence=evidence.confidence if evidence else draft.confidence_score,
            )
        )

