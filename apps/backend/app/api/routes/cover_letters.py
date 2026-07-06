from fastapi import APIRouter

from app.api.deps import DbSession, ERROR_RESPONSES
from app.core.codes import ErrorCode, SuccessCode
from app.core.errors import BusinessError
from app.repositories.experience_repository import ExperienceRepository
from app.schemas.common import ApiResponse
from app.schemas.cover_letter import CoverLetterDraftRequest, CoverLetterDraftResponse
from app.services.draft_generation import generate_draft

router = APIRouter()


@router.post(
    "/cover-letters/drafts",
    response_model=ApiResponse[CoverLetterDraftResponse, None],
    response_model_exclude_none=True,
    responses=ERROR_RESPONSES,
    summary="자기소개서 초안 생성",
    description="선택한 경험들의 구조화 내용(STAR·facet)만 근거로 문항에 답하는 초안을 생성합니다. "
    "원문에 없는 내용은 지어내지 않습니다.",
)
def create_cover_letter_draft(
    request: CoverLetterDraftRequest, db: DbSession
) -> ApiResponse[CoverLetterDraftResponse, None]:
    if not request.selected_experience_ids:
        raise BusinessError(ErrorCode.INVALID_NULL_DATA)
    repository = ExperienceRepository(db)
    experiences = []
    for experience_id in request.selected_experience_ids:
        experience = repository.get(experience_id)
        if experience is not None and experience.user_id == request.user_id:
            experiences.append(experience)
    if not experiences:
        raise BusinessError(ErrorCode.EXPERIENCE_NOT_FOUND)

    draft = generate_draft(request.question_text, experiences)
    data = CoverLetterDraftResponse(
        draft=draft, used_experience_ids=[experience.id for experience in experiences]
    )
    return ApiResponse.ok(SuccessCode.OK, data)
