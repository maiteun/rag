"""R5 선택 이벤트 캡처 테스트 (DB에 쓰므로 in-memory SQLite fixture 사용)."""

import pytest
from fastapi.testclient import TestClient

from app.core.errors import BusinessError
from app.db.session import get_db
from app.main import create_app
from app.models.selection_event import SelectionEvent
from app.schemas.selection import SelectionEventCreate
from app.services.selection_service import SelectionService

USER = "00000000-0000-0000-0000-000000000020"


def _base(**overrides):
    payload = {
        "user_id": USER,
        "question_type": "problem_solving",
        "job_description": "FastAPI 백엔드 개발",
        "question_text": "문제 해결 경험을 서술하시오.",
        "exposed_block_ids": ["b1", "b2", "b3"],
        "selected_block_id": "b1",
        "rejected_block_ids": ["b2", "b3"],
        "signals_snapshot": {"b1": {"has_metric": True, "has_role": True}},
    }
    payload.update(overrides)
    return SelectionEventCreate(**payload)


def test_record_selection_creates_row(db_session):
    event = SelectionService(db_session).record_selection(_base())
    assert event.id is not None
    stored = db_session.get(SelectionEvent, event.id)
    assert stored is not None
    assert stored.user_id == USER
    assert stored.question_type == "problem_solving"


def test_json_fields_round_trip(db_session):
    event = SelectionService(db_session).record_selection(_base())
    stored = db_session.get(SelectionEvent, event.id)
    assert stored.exposed_block_ids == ["b1", "b2", "b3"]
    assert stored.selected_block_id == "b1"
    assert stored.rejected_block_ids == ["b2", "b3"]


def test_signals_snapshot_round_trip(db_session):
    event = SelectionService(db_session).record_selection(_base())
    stored = db_session.get(SelectionEvent, event.id)
    assert stored.signals_snapshot == {"b1": {"has_metric": True, "has_role": True}}


def test_selected_must_be_in_exposed(db_session):
    with pytest.raises(BusinessError):
        SelectionService(db_session).record_selection(
            _base(selected_block_id="ghost", exposed_block_ids=["b1", "b2"])
        )


def test_skip_selection_is_allowed(db_session):
    # 사용자가 아무것도 안 고른 경우: selected None, rejected = 노출 전체
    event = SelectionService(db_session).record_selection(
        _base(selected_block_id=None, rejected_block_ids=["b1", "b2", "b3"])
    )
    stored = db_session.get(SelectionEvent, event.id)
    assert stored.selected_block_id is None
    assert stored.rejected_block_ids == ["b1", "b2", "b3"]


def _client(db_session) -> TestClient:
    app = create_app()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def test_api_post_selection(db_session):
    client = _client(db_session)
    response = client.post(
        "/api/selections",
        json={
            "user_id": USER,
            "question_type": "collaboration",
            "exposed_block_ids": ["b1", "b2"],
            "selected_block_id": "b2",
            "rejected_block_ids": ["b1"],
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["data"]["selection_id"]
    # 저장 확인
    assert db_session.get(SelectionEvent, body["data"]["selection_id"]) is not None


def test_api_post_rejects_selected_not_exposed(db_session):
    client = _client(db_session)
    response = client.post(
        "/api/selections",
        json={
            "user_id": USER,
            "exposed_block_ids": ["b1", "b2"],
            "selected_block_id": "ghost",
        },
    )
    assert response.status_code == 400
    assert response.json()["code"] == "SEL_400_001"
