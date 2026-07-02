from fastapi.testclient import TestClient

from app.db.session import get_db
from app.main import create_app
from app.models.source_document import SourceDocument
from app.services.pdf_text_extraction_service import PdfTextExtractionService


def test_pdf_upload_processes_through_experience_pipeline(db_session, monkeypatch):
    monkeypatch.setattr(
        PdfTextExtractionService,
        "extract",
        lambda self, content: "FastAPI and PostgreSQL project improved response time by 30%.",
    )

    app = create_app()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    response = client.post(
        "/api/documents/pdf",
        data={"user_id": "00000000-0000-0000-0000-000000000002", "title": "Portfolio PDF"},
        files={"file": ("portfolio.pdf", b"%PDF fake content", "application/pdf")},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["status"] == 201
    data = body["data"]
    assert data["status"] == "processed"
    assert data["experience_count"] >= 1
    assert data["experiences"]

    document = db_session.get(SourceDocument, data["document_id"])
    assert document is not None
    assert document.source_type == "pdf"
    assert document.original_filename == "portfolio.pdf"
    assert document.raw_text == "FastAPI and PostgreSQL project improved response time by 30%."


def test_pdf_upload_can_store_without_processing(db_session, monkeypatch):
    monkeypatch.setattr(PdfTextExtractionService, "extract", lambda self, content: "Stored PDF text")

    app = create_app()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    response = client.post(
        "/api/documents/pdf",
        data={
            "user_id": "00000000-0000-0000-0000-000000000003",
            "process_document": "false",
        },
        files={"file": ("memo.pdf", b"%PDF fake content", "application/pdf")},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert data["status"] == "uploaded"
    assert data["experience_count"] == 0
    assert data["experiences"] == []
