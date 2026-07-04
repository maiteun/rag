"""R6 선호 신호 학습 테스트. in-memory SQLite에 selection_events를 심고 검증."""

from types import SimpleNamespace
from uuid import uuid4

from app.models.selection_event import SelectionEvent
from app.models.user import User
from app.schemas.retrieval import RetrievalChunkResponse
from app.services.preference import compute_preference, compute_preferences_batch
from app.services.recommendation_engine import RagRecommendationEngine

USER = "00000000-0000-0000-0000-000000000030"


def _add_events(db, question_type, exposed, selected, times, user_id=USER):
    # selection_events.user_id 는 users FK — Postgres는 FK를 강제하므로 유저를 먼저 확정한다.
    # (SelectionEvent엔 User relationship이 없어 UOW가 삽입 순서를 보장하지 않음 → 명시 flush.)
    db.merge(User(id=user_id))
    db.flush()
    for _ in range(times):
        db.add(
            SelectionEvent(
                id=str(uuid4()),
                user_id=user_id,
                question_type=question_type,
                exposed_block_ids=list(exposed),
                selected_block_id=selected,
                rejected_block_ids=[b for b in exposed if b != selected],
            )
        )
    db.flush()


# ---- shrinkage 선택률 계산 ----

def test_cold_start_guard_below_min_observations(db_session):
    # 2번 노출 2번 선택 → MIN_OBSERVATIONS(3) 미만 → 학습 안 함
    _add_events(db_session, "collab", ["X"], "X", times=2)
    assert compute_preference(db_session, USER, "collab", "X") == 0.0


def test_positive_when_often_selected(db_session):
    # 10노출 9선택 → 양수(부스트)
    _add_events(db_session, "collab", ["X"], "X", times=9)
    _add_events(db_session, "collab", ["X"], None, times=1)
    assert compute_preference(db_session, USER, "collab", "X") > 0


def test_negative_when_rarely_selected(db_session):
    # 10노출 1선택 → 음수(페널티)
    _add_events(db_session, "collab", ["X"], "X", times=1)
    _add_events(db_session, "collab", ["X"], None, times=9)
    assert compute_preference(db_session, USER, "collab", "X") < 0


def test_neutral_at_half(db_session):
    # 10노출 5선택 → 중립(0 근처)
    _add_events(db_session, "collab", ["X"], "X", times=5)
    _add_events(db_session, "collab", ["X"], None, times=5)
    assert abs(compute_preference(db_session, USER, "collab", "X")) < 1e-9


def test_shrinkage_pulls_small_samples_toward_neutral(db_session):
    _add_events(db_session, "qa", ["S"], "S", times=3)  # 3/3
    _add_events(db_session, "qb", ["L"], "L", times=20)  # 20/20
    small = compute_preference(db_session, USER, "qa", "S")
    large = compute_preference(db_session, USER, "qb", "L")
    assert 0 < small < large  # 둘 다 양수지만 3/3이 덜 극단적


def test_question_type_separation(db_session):
    # 같은 block_id라도 문항유형 따라 선호 다름
    _add_events(db_session, "collaboration", ["B"], "B", times=10)  # 협업에선 선호
    _add_events(db_session, "problem_solving", ["B"], None, times=10)  # 문제해결에선 비선호
    assert compute_preference(db_session, USER, "collaboration", "B") > 0
    assert compute_preference(db_session, USER, "problem_solving", "B") < 0


def test_none_question_type_returns_zero(db_session):
    _add_events(db_session, "collab", ["X"], "X", times=10)
    assert compute_preference(db_session, USER, None, "X") == 0.0


def test_batch_matches_individual(db_session):
    _add_events(db_session, "collab", ["A", "B", "C"], "A", times=6)
    _add_events(db_session, "collab", ["A", "B", "C"], "B", times=4)
    batch = compute_preferences_batch(db_session, USER, "collab", ["A", "B", "C"])
    for block_id in ["A", "B", "C"]:
        assert batch[block_id] == compute_preference(db_session, USER, "collab", block_id)


# ---- R3 통합: preference가 rerank(w4=0.15)에 실려 순위에 영향 ----

def _flat_experience():
    return SimpleNamespace(
        has_metric=False, has_role=False, skills=[], competencies=[], sources=[],
        situation=None, action=None, result=None, completeness_score=0,
    )


def test_preference_influences_rerank_via_engine(db_session):
    # B는 협업 문항에서 선호(10/10), A는 비선호(10/0). 둘 다 노출 10.
    _add_events(db_session, "collaboration", ["A", "B"], "B", times=10)
    db_session.commit()

    class FakeRetrieval:
        def search(self, request):
            return [
                RetrievalChunkResponse(chunk_id="1", experience_id="A", chunk_text="x", similarity=0.90),
                RetrievalChunkResponse(chunk_id="2", experience_id="B", chunk_text="x", similarity=0.88),
                RetrievalChunkResponse(chunk_id="3", experience_id="C", chunk_text="x", similarity=0.20),
            ]

    exps = {"A": _flat_experience(), "B": _flat_experience(), "C": _flat_experience()}

    class FakeExpRepo:
        def get(self, eid):
            return exps[eid]

    engine = RagRecommendationEngine(db=db_session, retrieval=FakeRetrieval(), experiences=FakeExpRepo())

    # question_type 없음 → preference 0 → 검색점수 순 (A 먼저)
    baseline, _, _ = engine._run_pipeline(USER, "jd", "협업 경험", question_type=None)
    assert baseline[0].block_id == "A"

    # question_type="collaboration" → B 부스트 / A 페널티 → B 1위로 역전
    with_pref, _, _ = engine._run_pipeline(USER, "jd", "협업 경험", question_type="collaboration")
    order = [c.block_id for c in with_pref]
    assert order[0] == "B"
    pref = {c.block_id: c.preference for c in with_pref}
    assert pref["B"] > 0 and pref["A"] < 0
