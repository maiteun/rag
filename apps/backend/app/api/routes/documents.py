import json

from fastapi import APIRouter, File, Form, UploadFile, status

from app.api.deps import DbSession, ERROR_RESPONSES
from app.core.codes import ErrorCode, SuccessCode
from app.core.errors import BusinessError
from app.repositories.source_document_repository import SourceDocumentRepository
from app.schemas.common import ApiResponse
from app.schemas.document import (
    DocumentProcessingResultResponse,
    DocumentProcessResponse,
    PdfDocumentCreateResponse,
    TextDocumentCreateRequest,
    TextDocumentCreateResponse,
)
from app.services.document_processing_service import DocumentProcessingService
from app.services.document_service import DocumentService

router = APIRouter()


@router.post(
    "/documents/text",
    response_model=ApiResponse[TextDocumentCreateResponse, None],
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
    responses=ERROR_RESPONSES,
    summary="Create a text source document",
)
def create_text_document(
    request: TextDocumentCreateRequest, db: DbSession
) -> ApiResponse[TextDocumentCreateResponse, None]:
    document = DocumentService(db).create_text_document(request)
    data = TextDocumentCreateResponse(document_id=document.id, status=document.status)
    return ApiResponse.created(SuccessCode.CREATED, data)


@router.post(
    "/documents/pdf",
    response_model=ApiResponse[PdfDocumentCreateResponse, None],
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
    responses=ERROR_RESPONSES,
    summary="Upload a PDF source document and optionally process it into experiences",
)
async def create_pdf_document(
    db: DbSession,
    user_id: str = Form(...),
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
    process_document: bool = Form(default=True),
    metadata: str | None = Form(default=None),
) -> ApiResponse[PdfDocumentCreateResponse, None]:
    if file.content_type not in {None, "application/pdf"}:
        raise BusinessError(ErrorCode.INVALID_FILE_TYPE)
    parsed_metadata = _parse_metadata(metadata)
    content = await file.read()
    document = DocumentService(db).create_pdf_document(
        user_id=user_id,
        filename=file.filename,
        title=title,
        content=content,
        metadata=parsed_metadata,
    )
    if not process_document:
        data = PdfDocumentCreateResponse(document_id=document.id, status=document.status)
        return ApiResponse.created(SuccessCode.CREATED, data)

    doc_status, experience_count, question_count = DocumentProcessingService(db).process(document.id)
    experiences = DocumentProcessingService(db).summaries_for_document(document.id)
    data = PdfDocumentCreateResponse(
        document_id=document.id,
        status=doc_status,
        experience_count=experience_count,
        question_count=question_count,
        experiences=experiences,
    )
    return ApiResponse.created(SuccessCode.CREATED, data)


@router.post(
    "/documents/{document_id}/process",
    response_model=ApiResponse[DocumentProcessResponse, None],
    response_model_exclude_none=True,
    responses=ERROR_RESPONSES,
    summary="Process a source document into experiences",
)
def process_document(document_id: str, db: DbSession) -> ApiResponse[DocumentProcessResponse, None]:
    doc_status, experience_count, question_count = DocumentProcessingService(db).process(document_id)
    data = DocumentProcessResponse(
        document_id=document_id,
        status=doc_status,
        experience_count=experience_count,
        question_count=question_count,
    )
    return ApiResponse.ok(SuccessCode.OK, data)


@router.get(
    "/documents/{document_id}/processing-result",
    response_model=ApiResponse[DocumentProcessingResultResponse, None],
    response_model_exclude_none=True,
    responses=ERROR_RESPONSES,
    summary="Read document processing results",
)
def get_processing_result(document_id: str, db: DbSession) -> ApiResponse[DocumentProcessingResultResponse, None]:
    document = SourceDocumentRepository(db).get(document_id)
    if document is None:
        raise BusinessError(ErrorCode.DOCUMENT_NOT_FOUND)
    summaries = DocumentProcessingService(db).summaries_for_document(document_id)
    data = DocumentProcessingResultResponse(document_id=document.id, status=document.status, experiences=summaries)
    return ApiResponse.ok(SuccessCode.OK, data)


def _parse_metadata(metadata: str | None) -> dict:
    if not metadata:
        return {}
    try:
        parsed = json.loads(metadata)
    except json.JSONDecodeError as exc:
        raise BusinessError(ErrorCode.INVALID_METADATA) from exc
    if not isinstance(parsed, dict):
        raise BusinessError(ErrorCode.INVALID_METADATA)
    return parsed
