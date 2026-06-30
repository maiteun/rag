from sqlalchemy.orm import Session

from app.services.document_processing_service import DocumentProcessingService


def process_document_task(db: Session, document_id: str):
    return DocumentProcessingService(db).process(document_id)

