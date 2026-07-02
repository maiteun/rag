from fastapi import APIRouter

from app.api.deps import DbSession, ERROR_RESPONSES
from app.core.codes import ErrorCode, SuccessCode
from app.core.errors import BusinessError
from app.repositories.source_document_repository import SourceDocumentRepository
from app.schemas.common import ApiResponse
from app.schemas.resume import ResumeDetailResponse, ResumeListItem, ResumeListResponse

router = APIRouter()


@router.get(
    "/resumes",
    response_model=ApiResponse[ResumeListResponse, None],
    response_model_exclude_none=True,
    responses=ERROR_RESPONSES,
    summary="과거 이력서 목록 조회",
    description="source_type이 resume 또는 pdf인 문서를 이력서로 보고 최신순으로 돌려줍니다.",
)
def list_resumes(user_id: str, db: DbSession) -> ApiResponse[ResumeListResponse, None]:
    documents = SourceDocumentRepository(db).list_resumes_by_user(user_id)
    data = ResumeListResponse(resumes=[ResumeListItem.model_validate(doc) for doc in documents])
    return ApiResponse.ok(SuccessCode.OK, data)


@router.get(
    "/resumes/{resume_id}",
    response_model=ApiResponse[ResumeDetailResponse, None],
    response_model_exclude_none=True,
    responses=ERROR_RESPONSES,
    summary="과거 이력서 상세 조회",
    description="이력서 원문 텍스트까지 포함해서 돌려줍니다.",
)
def get_resume(resume_id: str, db: DbSession) -> ApiResponse[ResumeDetailResponse, None]:
    document = SourceDocumentRepository(db).get_resume(resume_id)
    if document is None:
        raise BusinessError(ErrorCode.RESUME_NOT_FOUND)
    data = ResumeDetailResponse.model_validate(document)
    return ApiResponse.ok(SuccessCode.OK, data)
