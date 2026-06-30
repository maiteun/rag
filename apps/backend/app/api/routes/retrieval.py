from fastapi import APIRouter

from app.api.deps import DbSession, ERROR_RESPONSES
from app.schemas.retrieval import RetrievalSearchRequest, RetrievalSearchResponse
from app.services.retrieval_service import RetrievalService

router = APIRouter()


@router.post(
    "/retrieval/search",
    response_model=RetrievalSearchResponse,
    responses=ERROR_RESPONSES,
    summary="Search RAG chunks for a user",
)
def search_retrieval(request: RetrievalSearchRequest, db: DbSession) -> RetrievalSearchResponse:
    return RetrievalSearchResponse(chunks=RetrievalService(db).search(request))

