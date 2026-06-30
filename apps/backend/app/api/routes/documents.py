from fastapi import APIRouter

from app.api.deps import DbSession, ERROR_RESPONSES
from app.core.errors import AppError
from app.repositories.source_document_repository import SourceDocumentRepository
from app.schemas.document import (
    DocumentProcessingResultResponse,
    DocumentProcessResponse,
    TextDocumentCreateRequest,
    TextDocumentCreateResponse,
)
from app.services.document_processing_service import DocumentProcessingService
from app.services.document_service import DocumentService

router = APIRouter()


@router.post(
    "/documents/text",
    response_model=TextDocumentCreateResponse,
    responses=ERROR_RESPONSES,
    summary="Create a text source document",
)
def create_text_document(request: TextDocumentCreateRequest, db: DbSession) -> TextDocumentCreateResponse:
    document = DocumentService(db).create_text_document(request)
    return TextDocumentCreateResponse(document_id=document.id, status=document.status)


@router.post(
    "/documents/{document_id}/process",
    response_model=DocumentProcessResponse,
    responses=ERROR_RESPONSES,
    summary="Process a source document into experiences",
)
def process_document(document_id: str, db: DbSession) -> DocumentProcessResponse:
    status, experience_count, question_count = DocumentProcessingService(db).process(document_id)
    return DocumentProcessResponse(
        document_id=document_id,
        status=status,
        experience_count=experience_count,
        question_count=question_count,
    )


@router.get(
    "/documents/{document_id}/processing-result",
    response_model=DocumentProcessingResultResponse,
    responses=ERROR_RESPONSES,
    summary="Read document processing results",
)
def get_processing_result(document_id: str, db: DbSession) -> DocumentProcessingResultResponse:
    document = SourceDocumentRepository(db).get(document_id)
    if document is None:
        raise AppError(404, "document_not_found", "Document not found.")
    summaries = DocumentProcessingService(db).summaries_for_document(document_id)
    return DocumentProcessingResultResponse(document_id=document.id, status=document.status, experiences=summaries)

