from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models.source_document import SourceDocument
from app.models.user import User
from app.repositories.source_document_repository import SourceDocumentRepository
from app.schemas.document import TextDocumentCreateRequest, VALID_SOURCE_TYPES
from app.services.pdf_text_extraction_service import PdfTextExtractionService


class DocumentService:
    def __init__(self, db: Session):
        self.db = db
        self.documents = SourceDocumentRepository(db)

    def create_text_document(self, request: TextDocumentCreateRequest) -> SourceDocument:
        if request.source_type not in VALID_SOURCE_TYPES:
            raise AppError(400, "invalid_source_type", "Unsupported source_type.")
        if not request.text.strip():
            raise AppError(400, "empty_text", "text must not be empty.")

        user = self.db.get(User, request.user_id)
        if user is None:
            user = User(id=request.user_id)
            self.db.add(user)
            self.db.flush()

        document = SourceDocument(
            id=str(uuid4()),
            user_id=request.user_id,
            source_type=request.source_type,
            title=request.title,
            raw_text=request.text,
            status="uploaded",
            doc_metadata=request.metadata,
        )
        self.documents.create(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def create_pdf_document(
        self,
        user_id: str,
        filename: str | None,
        content: bytes,
        title: str | None = None,
        metadata: dict | None = None,
        extractor: PdfTextExtractionService | None = None,
    ) -> SourceDocument:
        text = (extractor or PdfTextExtractionService()).extract(content)
        user = self.db.get(User, user_id)
        if user is None:
            user = User(id=user_id)
            self.db.add(user)
            self.db.flush()

        document = SourceDocument(
            id=str(uuid4()),
            user_id=user_id,
            source_type="pdf",
            title=title or filename,
            original_filename=filename,
            raw_text=text,
            status="uploaded",
            doc_metadata=metadata or {},
        )
        self.documents.create(document)
        self.db.commit()
        self.db.refresh(document)
        return document
