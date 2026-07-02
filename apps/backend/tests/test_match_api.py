from fastapi.testclient import TestClient

from app.db.session import get_db
from app.main import create_app
from app.schemas.match import MatchRecommendation
from app.services.match_service import MatchService


def _client(db_session) -> TestClient:
    app = create_app()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def test_create_match_and_poll_result(db_session):
    client = _client(db_session)

    response = client.post(
        "/api/matches",
        json={
            "user_id": "00000000-0000-0000-0000-000000000010",
            "job_description": "FastAPI 기반 백엔드 개발",
            "questions": ["문제 해결 경험을 서술하시오.", "협업 경험을 서술하시오."],
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    match_id = body["data"]["match_id"]
    assert body["data"]["status"] == "completed"

    response = client.get(f"/api/matches/{match_id}")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == match_id
    assert data["status"] == "completed"
    assert [q["text"] for q in data["questions"]] == [
        "문제 해결 경험을 서술하시오.",
        "협업 경험을 서술하시오.",
    ]
    assert all(q["recommendations"] == [] for q in data["questions"])


def test_get_match_not_found(db_session):
    client = _client(db_session)

    response = client.get("/api/matches/nonexistent")

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["code"] == "MAT_404_001"


def test_match_service_stores_engine_recommendations(db_session):
    class FakeEngine:
        def recommend(self, user_id, job_description, question):
            return [
                MatchRecommendation(experience_id="exp_1", rank=1, score=0.87, reason="문제 해결 과정이 명확함")
            ]

    from app.schemas.match import MatchCreateRequest

    service = MatchService(db_session, engine=FakeEngine())
    match_request = service.create(
        MatchCreateRequest(
            user_id="00000000-0000-0000-0000-000000000011",
            job_description="백엔드 개발",
            questions=["문제 해결 경험을 서술하시오."],
        )
    )

    detail = service.get(match_request.id)
    assert detail.status == "completed"
    assert detail.questions[0].recommendations[0].experience_id == "exp_1"
    assert detail.questions[0].recommendations[0].rank == 1


def test_match_marked_failed_when_engine_raises(db_session):
    class BrokenEngine:
        def recommend(self, user_id, job_description, question):
            raise RuntimeError("engine down")

    from app.schemas.match import MatchCreateRequest

    import pytest

    service = MatchService(db_session, engine=BrokenEngine())
    with pytest.raises(RuntimeError):
        service.create(
            MatchCreateRequest(
                user_id="00000000-0000-0000-0000-000000000012",
                job_description="백엔드 개발",
                questions=["문제 해결 경험을 서술하시오."],
            )
        )

    from app.models.match_request import MatchRequest
    from sqlalchemy import select

    stored = db_session.scalars(select(MatchRequest)).first()
    assert stored is not None
    assert stored.status == "failed"
