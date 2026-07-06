from fastapi.testclient import TestClient

from app.db.session import get_db
from app.main import create_app
from app.models.experience import Experience
from app.models.user import User


def _client(db_session) -> TestClient:
    app = create_app()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def _seed_experience(db_session, user_id: str, experience_id: str) -> str:
    db_session.merge(User(id=user_id))
    db_session.flush()
    experience = Experience(
        id=experience_id,
        user_id=user_id,
        title="기상 데이터 분석 공모전",
        situation="화재와 기상 데이터를 지역별로 결합해 분석해야 했다.",
        action="지형 기반으로 문제를 재정의하고 팀의 분석 기준을 조율했다.",
        result="지역별 맞춤 인사이트로 우수상을 받았다.",
        learned="문제를 어떻게 정의하느냐가 결과를 좌우한다는 것을 배웠다.",
        facets=[{"capability": "협업 조율", "label": "회의록과 기준 정리로 팀을 정렬"}],
    )
    db_session.add(experience)
    db_session.flush()
    return experience.id


def test_create_cover_letter_draft(db_session):
    user_id = "00000000-0000-0000-0000-000000000020"
    experience_id = _seed_experience(db_session, user_id, "exp-draft-1")
    client = _client(db_session)

    response = client.post(
        "/api/cover-letters/drafts",
        json={
            "user_id": user_id,
            "question_text": "협업 과정에서 갈등을 조율한 경험을 서술하시오.",
            "selected_experience_ids": [experience_id],
        },
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["draft"].strip()  # 초안이 비어 있지 않다
    assert data["used_experience_ids"] == [experience_id]


def test_draft_requires_selection(db_session):
    client = _client(db_session)
    response = client.post(
        "/api/cover-letters/drafts",
        json={"user_id": "u", "question_text": "질문", "selected_experience_ids": []},
    )
    assert response.status_code == 400


def test_draft_rejects_unknown_experience(db_session):
    client = _client(db_session)
    response = client.post(
        "/api/cover-letters/drafts",
        json={
            "user_id": "someone",
            "question_text": "질문",
            "selected_experience_ids": ["nonexistent"],
        },
    )
    assert response.status_code == 404
