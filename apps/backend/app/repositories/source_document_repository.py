from sqlalchemy.orm import Session

from app.models.source_document import SourceDocument


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

