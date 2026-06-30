from fastapi import APIRouter

from app.api.deps import DbSession, ERROR_RESPONSES
from app.core.errors import AppError
from app.repositories.experience_repository import ExperienceRepository
from app.schemas.experience import (
    ExperienceDetailResponse,
    ExperienceListItem,
    ExperienceListResponse,
    ExperienceQuestionResponse,
    ExperienceSourceResponse,
)

router = APIRouter()


@router.get(
    "/experiences",
    response_model=ExperienceListResponse,
    responses=ERROR_RESPONSES,
    summary="List experiences for a user",
)
def list_experiences(user_id: str, db: DbSession) -> ExperienceListResponse:
    experiences = ExperienceRepository(db).list_by_user(user_id)
    return ExperienceListResponse(experiences=[ExperienceListItem.model_validate(exp) for exp in experiences])


@router.get(
    "/experiences/{experience_id}",
    response_model=ExperienceDetailResponse,
    responses=ERROR_RESPONSES,
    summary="Read an experience with sources and questions",
)
def get_experience(experience_id: str, db: DbSession) -> ExperienceDetailResponse:
    experience = ExperienceRepository(db).get(experience_id)
    if experience is None:
        raise AppError(404, "experience_not_found", "Experience not found.")
    return ExperienceDetailResponse(
        id=experience.id,
        title=experience.title,
        summary=experience.summary,
        start_date=experience.start_date,
        end_date=experience.end_date,
        experience_type=experience.experience_type,
        organization=experience.organization,
        role=experience.role,
        situation=experience.situation,
        task=experience.task,
        action=experience.action,
        result=experience.result,
        learned=experience.learned,
        skills=experience.skills,
        competencies=experience.competencies,
        keywords=experience.keywords,
        completeness_score=experience.completeness_score,
        confidence_score=experience.confidence_score,
        sources=[
            ExperienceSourceResponse(
                source_document_id=source.source_document_id,
                title=source.source_document.title if source.source_document else None,
                excerpt=source.source_excerpt,
            )
            for source in experience.sources
        ],
        questions=[
            ExperienceQuestionResponse(
                id=question.id,
                question=question.question,
                question_type=question.question_type,
                reason=question.reason,
                priority=question.priority,
                status=question.status,
            )
            for question in experience.questions
        ],
    )

