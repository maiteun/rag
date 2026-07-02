from fastapi import APIRouter

from app.api.deps import DbSession, ERROR_RESPONSES
from app.core.codes import SuccessCode
from app.schemas.common import ApiResponse
from app.schemas.retrieval import RetrievalSearchRequest, RetrievalSearchResponse
from app.services.retrieval_service import RetrievalService

router = APIRouter()


@router.post(
    "/retrieval/search",
    response_model=ApiResponse[RetrievalSearchResponse, None],
    response_model_exclude_none=True,
    responses=ERROR_RESPONSES,
    summary="경험 청크 검색",
    description="질의를 임베딩해서 사용자의 경험 청크를 유사도 순으로 돌려줍니다.",
)
def search_retrieval(request: RetrievalSearchRequest, db: DbSession) -> ApiResponse[RetrievalSearchResponse, None]:
    data = RetrievalSearchResponse(chunks=RetrievalService(db).search(request))
    return ApiResponse.ok(SuccessCode.OK, data)
