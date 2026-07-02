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
    summary="Search RAG chunks for a user",
)
def search_retrieval(request: RetrievalSearchRequest, db: DbSession) -> ApiResponse[RetrievalSearchResponse, None]:
    data = RetrievalSearchResponse(chunks=RetrievalService(db).search(request))
    return ApiResponse.ok(SuccessCode.OK, data)
