from datetime import datetime, timezone

from app.models.experience_chunk import ExperienceChunk
from app.models.experience import Experience
from app.models.experience_question import ExperienceQuestion
from app.models.user import User
from app.repositories.experience_repository import ExperienceRepository
from app.repositories.question_repository import QuestionRepository
from app.schemas.document import TextDocumentCreateRequest
from app.schemas.retrieval import RetrievalSearchRequest
from app.services.document_processing_service import DocumentProcessingService
from app.services.document_service import DocumentService
from app.services.question_answer_service import QuestionAnswerService
from app.services.retrieval_service import RetrievalService


def test_document_processing_pipeline_and_answer_flow(db_session):
    user_id = "00000000-0000-0000-0000-000000000000"
    document = DocumentService(db_session).create_text_document(
        TextDocumentCreateRequest(
            user_id=user_id,
            source_type="cover_letter",
            title="2025 application",
            text="FastAPI와 PostgreSQL 기반 추천 API 프로젝트를 진행했습니다. 문제를 분석하고 API를 구현했습니다.",
        )
    )

    status, experience_count, question_count = DocumentProcessingService(db_session).process(document.id)
    assert status == "processed"
    assert experience_count >= 1
    assert question_count >= 1

    experiences = ExperienceRepository(db_session).list_by_document(document.id)
    assert experiences
    experience = experiences[0]
    assert experience.sources

    questions = experience.questions
    assert questions
    question_id = questions[0].id
    previous_score = float(experience.completeness_score)

    _, experience_id, updated_score = QuestionAnswerService(db_session).answer(
        question_id,
        "추천 API 적용 후 평균 응답 시간이 1.8초에서 0.9초로 감소했습니다.",
    )
    assert experience_id == experience.id
    assert updated_score > previous_score or updated_score >= 100
    assert QuestionRepository(db_session).get(question_id).status == "answered"

    chunks = db_session.query(ExperienceChunk).filter(ExperienceChunk.experience_id == experience.id).all()
    assert chunks
    assert all(chunk.embedding is not None for chunk in chunks)

    results = RetrievalService(db_session).search(
        RetrievalSearchRequest(user_id=user_id, queries=["FastAPI 성능 개선 경험"], top_k=5)
    )
    assert results
    assert results[0].experience_id == experience.id


def test_date_answer_updates_experience_dates(db_session):
    user_id = "date-answer-user"
    experience_id = "date-answer-exp"
    question_id = "date-answer-question"
    db_session.add(User(id=user_id))
    db_session.add(
        Experience(
            id=experience_id,
            user_id=user_id,
            title="Database project",
            summary="Built a course archive service.",
            experience_type="project",
            role="backend developer",
            action="Designed the schema and built APIs.",
            result="Reduced search latency from 1.8s to 0.6s.",
            skills=["FastAPI", "PostgreSQL"],
            competencies=["backend development"],
            keywords=["archive"],
            has_metric=True,
            has_role=True,
            has_result=True,
            completeness_score=90,
            confidence_score=80,
            status="confirmed",
        )
    )
    db_session.add(
        ExperienceQuestion(
            id=question_id,
            user_id=user_id,
            experience_id=experience_id,
            question="What were the exact start and end dates?",
            question_type="date",
            reason="The exact period is missing.",
            priority=1,
            status="pending",
            created_at=datetime.now(timezone.utc),
        )
    )
    db_session.commit()

    _, updated_experience_id, score = QuestionAnswerService(db_session).answer(
        question_id,
        "2026년 1월 1일부터 2026년 1월 2일",
    )

    experience = ExperienceRepository(db_session).get(experience_id)
    question = QuestionRepository(db_session).get(question_id)

    assert updated_experience_id == experience_id
    assert str(experience.start_date) == "2026-01-01"
    assert str(experience.end_date) == "2026-01-02"
    assert "2026년 1월 1일부터" not in experience.action
    assert question.status == "answered"
    assert question.answer == "2026년 1월 1일부터 2026년 1월 2일"
    assert score == 100
