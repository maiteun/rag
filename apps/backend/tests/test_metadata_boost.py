"""R2 ⑤ 메타데이터 소프트 부스트 테스트.

핵심 성질: 소프트 부스트(하드 필터 아님) + skills 주력 + 벡터 주력을 뒤엎지 않음 + date 없음.
"""

import inspect
from types import SimpleNamespace

from app.schemas.retrieval import RetrievalChunkResponse
from app.services.metadata_boost import (
    BOOST_SKILL,
    BOOST_TYPE,
    MAX_SKILL_OVERLAP,
    compute_metadata_boost,
    extract_query_terms,
)
from app.services.recommendation_engine import RagRecommendationEngine
from app.services.reranking import RerankCandidate, rerank

USER = "22222222-0000-0000-0000-000000000001"


# ---- compute_metadata_boost 순수 함수 ----

def test_skill_overlap_boost_scales_with_count():
    req = {"python", "fastapi", "postgresql", "docker"}
    b0, _ = compute_metadata_boost([], None, req)
    b1, _ = compute_metadata_boost(["python"], None, req)
    b2, _ = compute_metadata_boost(["python", "fastapi"], None, req)
    b3, _ = compute_metadata_boost(["python", "fastapi", "postgresql"], None, req)
    assert b0 == 0.0
    assert b1 < b2 < b3  # 겹침 수에 비례해 커짐
    assert abs(b1 - (1 / MAX_SKILL_OVERLAP) * BOOST_SKILL) < 1e-9
    assert abs(b3 - BOOST_SKILL) < 1e-9  # 3개 = 포화


def test_skill_boost_saturates_at_max_overlap():
    req = {"a", "b", "c", "d", "e"}
    b3, _ = compute_metadata_boost(["a", "b", "c"], None, req)
    b5, _ = compute_metadata_boost(["a", "b", "c", "d", "e"], None, req)
    assert b3 == b5 == BOOST_SKILL  # MAX_SKILL_OVERLAP 이상은 포화


def test_matching_is_case_and_whitespace_insensitive():
    boost, signals = compute_metadata_boost(["  FastAPI ", "PYTHON"], None, {"fastapi", "python"})
    assert abs(boost - (2 / MAX_SKILL_OVERLAP) * BOOST_SKILL) < 1e-9
    assert "skill_boost:fastapi" in signals and "skill_boost:python" in signals


def test_no_overlap_returns_zero_not_exclusion():
    # 겹침 0 → 부스트 0. (제외가 아님을 rerank/engine 테스트에서 확인)
    boost, signals = compute_metadata_boost(["figma", "sketch"], None, {"python", "fastapi"})
    assert boost == 0.0
    assert signals == []


def test_empty_requirement_terms_returns_zero():
    boost, signals = compute_metadata_boost(["python"], "project", set())
    assert boost == 0.0 and signals == []


def test_type_boost_fires_when_type_in_terms():
    boost, signals = compute_metadata_boost([], "project", {"project", "backend"})
    assert boost == BOOST_TYPE
    assert "type_boost:project" in signals


def test_type_boost_absent_when_no_match():
    boost, _ = compute_metadata_boost([], "project", {"backend"})
    assert boost == 0.0


def test_skill_and_type_boost_combine():
    boost, _ = compute_metadata_boost(["python"], "project", {"python", "project"})
    assert abs(boost - ((1 / MAX_SKILL_OVERLAP) * BOOST_SKILL + BOOST_TYPE)) < 1e-9


def test_extract_query_terms_tokenizes_and_lowercases():
    terms = extract_query_terms(["FastAPI로 성능 개선", "PostgreSQL, Docker"])
    assert {"fastapi", "postgresql", "docker", "성능", "개선"} <= terms


def test_no_date_input_sealed():
    # 빌드타임 날짜 환각 이슈로 date는 봉인 — 부스트 함수가 date를 입력으로 받지 않는다.
    # (경험 date/period가 인자 목록에 없으므로 부스트 계산에 date가 개입할 경로 자체가 없음.)
    params = set(inspect.signature(compute_metadata_boost).parameters)
    assert params == {"experience_skills", "experience_type", "requirement_terms"}
    assert not any("date" in name or "period" in name for name in params)


# ---- rerank 통합: 부스트가 순위에 반영되되 소프트(제외 없음) ----

def _cand(block_id, search_score, boost=0.0):
    return RerankCandidate(block_id=block_id, search_score=search_score, metadata_boost=boost)


def test_boost_lifts_rank_when_vector_scores_tie():
    # 벡터 점수 동일 → 정규화 relevance 동일 → 부스트가 순위 결정
    result = rerank([_cand("A", 0.8, boost=0.0), _cand("B", 0.8, boost=BOOST_SKILL)])
    assert result[0].block_id == "B"
    assert result[0].signals["metadata_boost"] == round(BOOST_SKILL, 4)


def test_zero_boost_candidate_still_present():
    # 소프트 = 하드 필터 아님: 부스트 0이어도 결과에서 제외되지 않는다.
    result = rerank([_cand("A", 0.8, boost=BOOST_SKILL), _cand("B", 0.5, boost=0.0)])
    ids = {r.block_id for r in result}
    assert ids == {"A", "B"}


def test_boost_does_not_override_strong_vector_gap():
    # 벡터 점수 크게 차이(정규화 후 relevance 1.0 vs 0.0) → 최대 부스트로도 역전 불가
    max_boost = BOOST_SKILL + BOOST_TYPE
    result = rerank([_cand("hi", 0.95, boost=0.0), _cand("lo", 0.10, boost=max_boost)])
    assert result[0].block_id == "hi"


# ---- 엔진 배선: skills 매칭이 실제 순위에 반영 ----

def _exp(skills, experience_type="project"):
    return SimpleNamespace(
        has_metric=False, has_role=False, skills=skills, competencies=[], sources=[],
        situation=None, action=None, result=None, completeness_score=0,
        experience_type=experience_type,
    )


def test_engine_wires_skill_boost():
    # 두 경험 벡터 유사도 동일. 쿼리에 'FastAPI' → FastAPI 보유 경험이 부스트로 1위.
    class FakeRetrieval:
        def search(self, request):
            return [
                RetrievalChunkResponse(chunk_id="1", experience_id="A", chunk_text="x", similarity=0.80),
                RetrievalChunkResponse(chunk_id="2", experience_id="B", chunk_text="x", similarity=0.80),
            ]

    exps = {"A": _exp(skills=["Figma"]), "B": _exp(skills=["FastAPI"])}

    class FakeExpRepo:
        def get(self, eid):
            return exps[eid]

    engine = RagRecommendationEngine(db=None, retrieval=FakeRetrieval(), experiences=FakeExpRepo())
    reranked, _, _ = engine._run_pipeline(USER, "백엔드 개발", "FastAPI 성능 개선 경험")
    assert reranked[0].block_id == "B"
    assert reranked[0].signals["metadata_boost"] > 0
    # A는 부스트 0이지만 후보에서 제외되지 않음 (소프트)
    assert {c.block_id for c in reranked} == {"A", "B"}


def test_engine_uses_facet_capability_for_boost_and_signals():
    class FakeRetrieval:
        def search(self, request):
            return [
                RetrievalChunkResponse(
                    chunk_id="facet-1",
                    experience_id="A",
                    chunk_text="x",
                    chunk_type="facet",
                    similarity=0.80,
                    metadata={
                        "facet_capability": "collaboration",
                        "facet_label": "coordinated handoffs",
                        "facet_details": ["meeting notes"],
                        "facet_evidence": ["coordinated the team"],
                    },
                ),
                RetrievalChunkResponse(
                    chunk_id="summary-2",
                    experience_id="B",
                    chunk_text="x",
                    chunk_type="experience_summary",
                    similarity=0.80,
                ),
            ]

    exps = {
        "A": SimpleNamespace(
            has_metric=False,
            has_role=False,
            skills=[],
            competencies=[],
            facets=[{"capability": "collaboration"}],
            sources=[],
            situation=None,
            action=None,
            result=None,
            completeness_score=0,
            experience_type="project",
        ),
        "B": _exp(skills=[], experience_type="project"),
    }

    class FakeExpRepo:
        def get(self, eid):
            return exps[eid]

    engine = RagRecommendationEngine(db=None, retrieval=FakeRetrieval(), experiences=FakeExpRepo())
    reranked, _, meta_by_id = engine._run_pipeline(USER, "jd", "collaboration experience")

    assert reranked[0].block_id == "A"
    assert reranked[0].signals["metadata_boost"] > 0
    assert "skill_boost:collaboration" in reranked[0].signals["metadata_signals"]
    assert reranked[0].signals["retrieval"]["facet_capability"] == "collaboration"
    assert "coordinated the team" in meta_by_id["A"].sources
