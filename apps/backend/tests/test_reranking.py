"""R3 리랭킹 단위 테스트 (순수 함수 — 외부 의존 없음)."""

from app.services.reranking import RerankCandidate, rerank


def _cand(block_id, search_score, **kw):
    return RerankCandidate(block_id=block_id, search_score=search_score, **kw)


# ---- relevance 정규화 ----

def test_relevance_minmax_normalization():
    result = rerank(
        [_cand("a", 0.9), _cand("b", 0.5), _cand("c", 0.1)],
        w2=0, w5=0, w4=0,  # relevance만 남겨 비교
    )
    by_id = {r.block_id: r for r in result}
    assert by_id["a"].relevance == 1.0
    assert by_id["b"].relevance == 0.5
    assert by_id["c"].relevance == 0.0


def test_all_equal_scores_relevance_all_one():
    result = rerank([_cand("a", 0.5), _cand("b", 0.5), _cand("c", 0.5)])
    assert all(r.relevance == 1.0 for r in result)  # 0으로 나누기 방지


# ---- trust 규칙 ----

def test_trust_upper_bound():
    # metric + role + sources 2개 + completeness 1.0 → 0.4+0.2+0.15+0.1+0.1+0.15=1.10 → clip 1.0
    r = rerank([_cand("a", 1.0, has_metric=True, has_role=True, sources_count=2, completeness=1.0)])[0]
    assert r.trust == 1.0


def test_trust_base_only():
    # 아무 신호 없음 (sources 0) → base 0.4
    r = rerank([_cand("a", 1.0)])[0]
    assert r.trust == 0.4


# ---- frequency ----

def test_frequency_scaling():
    one = rerank([_cand("a", 1.0, sources_count=1)])[0]
    three = rerank([_cand("a", 1.0, sources_count=3)])[0]
    five = rerank([_cand("a", 1.0, sources_count=5)])[0]
    assert round(one.frequency, 2) == 0.33
    assert three.frequency == 1.0
    assert five.frequency == 1.0  # 상한


# ---- 가중합 역전 ----

def test_weighted_sum_can_reverse_rank():
    # b: relevance 약간 낮지만(0.944) trust·frequency 최고 → a(relevance 1.0, 신호 없음)를 역전
    candidates = [
        _cand("a", 1.0),  # rel 1.0, trust 0.4, freq 0
        _cand("b", 0.95, has_metric=True, has_role=True, sources_count=2, completeness=1.0),
        _cand("c", 0.1),  # rel 0.0
    ]
    result = rerank(candidates)  # 기본 가중치
    assert result[0].block_id == "b"  # 검색점수는 a가 더 높지만 b가 1위
    assert result[1].block_id == "a"
    assert result[2].block_id == "c"


def test_weights_zero_falls_back_to_relevance_order():
    result = rerank(
        [_cand("a", 0.2, has_metric=True), _cand("b", 0.8), _cand("c", 0.5)],
        w2=0, w5=0, w4=0,
    )
    assert [r.block_id for r in result] == ["b", "c", "a"]  # 검색점수 순


# ---- preference (w4=0 이라 결과 불변) ----

def test_preference_ignored_when_w4_zero():
    without = rerank([_cand("a", 1.0), _cand("b", 0.5)])
    with_pref = rerank([_cand("a", 1.0, preference=0.9), _cand("b", 0.5, preference=0.9)])
    assert [r.final_score for r in without] == [r.final_score for r in with_pref]


# ---- 엣지 ----

def test_single_candidate():
    result = rerank([_cand("solo", 0.7)])
    assert len(result) == 1
    assert result[0].relevance == 1.0  # 단독 → 1.0


def test_empty_list():
    assert rerank([]) == []
