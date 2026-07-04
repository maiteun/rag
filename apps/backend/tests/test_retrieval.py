"""R2 pgvector 벡터 검색 테스트.

fake 임베딩은 텍스트→벡터가 결정적이지만 방향을 통제하기 어렵다. 그래서
벡터 정렬 자체는 **손으로 만든 알려진 임베딩 + 직접 넣은 질의 벡터**로 검증한다.
(임베딩 단계를 건너뛰고 pgvector `<=>` 순서만 본다.)
"""

from uuid import uuid4

from app.models.experience_chunk import ExperienceChunk
from app.models.user import User
from app.repositories.chunk_repository import ChunkRepository
from app.schemas.retrieval import RetrievalSearchRequest
from app.services.retrieval_service import RetrievalService

DIM = 1536


def _vec(*head: float) -> list[float]:
    """앞자리만 지정하고 나머지는 0인 1536차원 벡터."""
    v = [0.0] * DIM
    for i, x in enumerate(head):
        v[i] = float(x)
    return v


def _add_chunk(db, user_id, chunk_id, embedding, experience_id=None):
    db.add(
        ExperienceChunk(
            id=chunk_id,
            user_id=user_id,
            experience_id=experience_id,
            chunk_text=f"chunk {chunk_id}",
            embedding=embedding,
        )
    )


def _seed_user(db, user_id):
    db.merge(User(id=user_id))
    db.flush()


# ---- repository: pgvector 코사인 거리 정렬 ----

def test_search_by_vector_orders_by_cosine_distance(db_session):
    user = "11111111-0000-0000-0000-000000000001"
    _seed_user(db_session, user)
    # query=[1,0]. A=[1,0](sim1), B=[0.6,0.8](sim0.6), C=[0,1](sim0)
    _add_chunk(db_session, user, "A", _vec(1, 0))
    _add_chunk(db_session, user, "B", _vec(0.6, 0.8))
    _add_chunk(db_session, user, "C", _vec(0, 1))
    db_session.flush()

    results = ChunkRepository(db_session).search_by_vector(user, _vec(1, 0), top_k=10)
    ids = [chunk.id for chunk, _ in results]
    assert ids == ["A", "B", "C"]  # 가까운 순
    sims = {chunk.id: 1.0 - dist for chunk, dist in results}
    assert abs(sims["A"] - 1.0) < 1e-6
    assert abs(sims["B"] - 0.6) < 1e-6
    assert abs(sims["C"] - 0.0) < 1e-6


def test_search_by_vector_excludes_null_embeddings(db_session):
    user = "11111111-0000-0000-0000-000000000002"
    _seed_user(db_session, user)
    _add_chunk(db_session, user, "A", _vec(1, 0))
    _add_chunk(db_session, user, "N", None)  # 임베딩 없음 → 비교 불가 → 제외
    db_session.flush()

    ids = [c.id for c, _ in ChunkRepository(db_session).search_by_vector(user, _vec(1, 0), top_k=10)]
    assert ids == ["A"]


def test_search_by_vector_respects_top_k(db_session):
    user = "11111111-0000-0000-0000-000000000003"
    _seed_user(db_session, user)
    _add_chunk(db_session, user, "A", _vec(1, 0))
    _add_chunk(db_session, user, "B", _vec(0.6, 0.8))
    _add_chunk(db_session, user, "C", _vec(0, 1))
    db_session.flush()

    results = ChunkRepository(db_session).search_by_vector(user, _vec(1, 0), top_k=2)
    assert [c.id for c, _ in results] == ["A", "B"]


def test_search_by_vector_isolates_user(db_session):
    me = "11111111-0000-0000-0000-000000000004"
    other = "11111111-0000-0000-0000-000000000005"
    _seed_user(db_session, me)
    _seed_user(db_session, other)
    _add_chunk(db_session, me, "mine", _vec(1, 0))
    _add_chunk(db_session, other, "theirs", _vec(1, 0))
    db_session.flush()

    ids = [c.id for c, _ in ChunkRepository(db_session).search_by_vector(me, _vec(1, 0), top_k=10)]
    assert ids == ["mine"]


# ---- service: 다중 질의 max 병합 ----

class _StubEmbeddings:
    """질의 텍스트 → 고정 벡터 매핑 (임베딩 통제)."""

    def __init__(self, mapping):
        self.mapping = mapping

    def embed(self, text: str) -> list[float]:
        return self.mapping[text]


def test_search_merges_multiple_queries_by_max_similarity(db_session):
    user = "11111111-0000-0000-0000-000000000006"
    _seed_user(db_session, user)
    _add_chunk(db_session, user, "A", _vec(1, 0))  # q1에 가까움
    _add_chunk(db_session, user, "C", _vec(0, 1))  # q2에 가까움
    db_session.flush()

    embeddings = _StubEmbeddings({"q1": _vec(1, 0), "q2": _vec(0, 1)})
    service = RetrievalService(db_session, embeddings=embeddings)
    results = service.search(RetrievalSearchRequest(user_id=user, queries=["q1", "q2"], top_k=10))

    sims = {r.chunk_id: r.similarity for r in results}
    # A는 q1에서, C는 q2에서 각각 최대 유사도 1 → 둘 다 상위
    assert abs(sims["A"] - 1.0) < 1e-6
    assert abs(sims["C"] - 1.0) < 1e-6


def test_search_empty_when_no_chunks(db_session):
    user = "11111111-0000-0000-0000-000000000007"
    _seed_user(db_session, user)
    embeddings = _StubEmbeddings({"q": _vec(1, 0)})
    service = RetrievalService(db_session, embeddings=embeddings)
    assert service.search(RetrievalSearchRequest(user_id=user, queries=["q"], top_k=10)) == []
