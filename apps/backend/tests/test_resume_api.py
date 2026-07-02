from uuid import uuid4

from fastapi.testclient import TestClient

from app.db.session import get_db
from app.main import create_app
from app.models.source_document import SourceDocument
from app.models.user import User


def _client(db_session) -> TestClient:
    app = create_app()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def _create_document(db_session, user_id: str, source_type: str, title: str) -> SourceDocument:
    document = SourceDocument(
        id=str(uuid4()),
        user_id=user_id,
        source_type=source_type,
        title=title,
        raw_text="이력서 본문",
        status="uploaded",
        doc_metadata={},
    )
    db_session.add(document)
    db_session.commit()
    return document


def test_list_resumes_filters_by_source_type(db_session):
    user_id = "00000000-0000-0000-0000-000000000020"
    db_session.add(User(id=user_id))
    db_session.commit()
    _create_document(db_session, user_id, "resume", "이력서 v1")
    _create_document(db_session, user_id, "pdf", "이력서 v2")
    _create_document(db_session, user_id, "memo", "메모")

    client = _client(db_session)
    response = client.get("/api/resumes", params={"user_id": user_id})

    assert response.status_code == 200
    resumes = response.json()["data"]["resumes"]
    assert {item["title"] for item in resumes} == {"이력서 v1", "이력서 v2"}


def test_get_resume_detail(db_session):
    user_id = "00000000-0000-0000-0000-000000000021"
    db_session.add(User(id=user_id))
    db_session.commit()
    document = _create_document(db_session, user_id, "resume", "이력서 v1")

    client = _client(db_session)
    response = client.get(f"/api/resumes/{document.id}")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == document.id
    assert data["raw_text"] == "이력서 본문"


def test_get_resume_rejects_non_resume_document(db_session):
    user_id = "00000000-0000-0000-0000-000000000022"
    db_session.add(User(id=user_id))
    db_session.commit()
    document = _create_document(db_session, user_id, "memo", "메모")

    client = _client(db_session)
    response = client.get(f"/api/resumes/{document.id}")

    assert response.status_code == 404
    assert response.json()["code"] == "RSM_404_001"
