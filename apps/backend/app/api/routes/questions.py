from fastapi import APIRouter

from app.api.deps import DbSession, ERROR_RESPONSES
from app.core.codes import SuccessCode
from app.schemas.common import ApiResponse
from app.schemas.question import QuestionAnswerRequest, QuestionAnswerResponse
from app.services.question_answer_service import QuestionAnswerService

router = APIRouter()


@router.post(
    "/experience-questions/{question_id}/answer",
    response_model=ApiResponse[QuestionAnswerResponse, None],
    response_model_exclude_none=True,
    responses=ERROR_RESPONSES,
    summary="Answer a follow-up question and update the experience",
)
def answer_question(
    question_id: str, request: QuestionAnswerRequest, db: DbSession
) -> ApiResponse[QuestionAnswerResponse, None]:
    resolved_question_id, experience_id, score = QuestionAnswerService(db).answer(question_id, request.answer)
    data = QuestionAnswerResponse(
        question_id=resolved_question_id,
        experience_id=experience_id,
        status="answered",
        updated_completeness_score=score,
    )
    return ApiResponse.ok(SuccessCode.OK, data)
