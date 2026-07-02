from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.source_document import SourceDocument

RESUME_SOURCE_TYPES = {"resume", "pdf"}


class SourceDocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, document: SourceDocument) -> SourceDocument:
        self.db.add(document)
        self.db.flush()
        return document

    def get(self, document_id: str) -> SourceDocument | None:
        return self.db.get(SourceDocument, document_id)

    def update_status(self, document: SourceDocument, status: str) -> SourceDocument:
        document.status = status
        self.db.flush()
        return document

    def list_resumes_by_user(self, user_id: str) -> list[SourceDocument]:
        stmt = (
            select(SourceDocument)
            .where(
                SourceDocument.user_id == user_id,
                SourceDocument.source_type.in_(RESUME_SOURCE_TYPES),
            )
            .order_by(SourceDocument.created_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def get_resume(self, document_id: str) -> SourceDocument | None:
        document = self.db.get(SourceDocument, document_id)
        if document is None or document.source_type not in RESUME_SOURCE_TYPES:
            return None
        return document

