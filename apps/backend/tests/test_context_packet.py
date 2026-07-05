"""R7 컨텍스트 패킷 단위 테스트 (순수 함수)."""

from app.services.context_packet import ExperienceMeta, build_context_packet
from app.services.reranking import RerankedCandidate


def _cand(block_id, final_score=0.5, relevance=1.0, trust=0.7, frequency=0.0):
    return RerankedCandidate(
        block_id=block_id,
        final_score=final_score,
        relevance=relevance,
        trust=trust,
        frequency=frequency,
        preference=0.0,
    )


def _packet(reranked, recommended_ids, experiences, requirements=None, question_type="problem_solving"):
    return build_context_packet(
        question="문제 해결 경험을 서술하시오.",
        question_type=question_type,
        requirements=requirements or [],
        reranked=reranked,
        recommended_ids=recommended_ids,
        experiences=experiences,
    )


# ---- fit 구간 ----

def test_fit_bands():
    reranked = [_cand("hi", 0.82), _cand("mid", 0.55), _cand("lo", 0.30)]
    packet = _packet(reranked, ["hi", "mid", "lo"], {})
    fits = {b.block_id: b.fit for b in packet.recommended}
    assert fits == {"hi": "높음", "mid": "중간", "lo": "낮음"}


# ---- reason_signals ----

def test_reason_signals_are_tags_not_sentences():
    meta = {"a": ExperienceMeta(has_metric=True, has_role=True, skills=["XGBoost", "Python"], competencies=[])}
    packet = _packet([_cand("a")], ["a"], meta, requirements=["XGBoost", "협업"])
    signals = packet.recommended[0].reason_signals
    assert "has_metric" in signals
    assert "role_clear" in signals
    assert "skill_match:XGBoost" in signals
    assert "skill_match:Python" not in signals  # Python은 요구사항에 없음
    # 태그 포맷 검증: 완성 문장 아님 (고정 태그거나 prefix 태그)
    for s in signals:
        assert s in {"has_metric", "role_clear"} or s.startswith(("skill_match:", "competency_match:"))
        assert "." not in s and "습니다" not in s


def test_competency_match_signal():
    meta = {"a": ExperienceMeta(competencies=["문제 재정의", "협업"])}
    packet = _packet([_cand("a")], ["a"], meta, requirements=["협업 능력"])
    assert "competency_match:협업" in packet.recommended[0].reason_signals


# ---- missing ----

def test_missing_when_signals_absent():
    meta = {"a": ExperienceMeta(has_metric=False, has_role=False, sources=[])}
    packet = _packet([_cand("a")], ["a"], meta)
    assert packet.recommended[0].missing == ["성과 수치 없음", "본인 역할 불명확", "출처 없음"]


def test_missing_empty_when_all_present():
    meta = {"a": ExperienceMeta(has_metric=True, has_role=True, sources=["doc1"])}
    packet = _packet([_cand("a")], ["a"], meta)
    assert packet.recommended[0].missing == []


# ---- framing_hint ----

def test_framing_hint_when_star_complete():
    meta = {
        "a": ExperienceMeta(has_metric=True, has_role=True, sources=["d"], star_complete=True),
        "b": ExperienceMeta(star_complete=False),
    }
    packet = _packet([_cand("a"), _cand("b")], ["a", "b"], meta)
    hints = {b.block_id: b.framing_hint for b in packet.recommended}
    assert hints["a"] == "문제정의 → 행동 → 결과"
    assert hints["b"] is None


# ---- uncovered_requirements ----

def test_uncovered_requirements():
    meta = {"a": ExperienceMeta(skills=["협업"], competencies=["정량성과"])}
    packet = _packet([_cand("a")], ["a"], meta, requirements=["협업", "정량성과", "대용량처리"])
    assert packet.uncovered_requirements == ["대용량처리"]


def test_no_uncovered_when_all_covered():
    meta = {"a": ExperienceMeta(skills=["협업", "정량성과"])}
    packet = _packet([_cand("a")], ["a"], meta, requirements=["협업", "정량성과"])
    assert packet.uncovered_requirements == []


# ---- not_recommended ----

def test_not_recommended_gets_tags():
    reranked = [
        _cand("r1", relevance=1.0, trust=0.8),
        _cand("r2", relevance=0.9, trust=0.7),
        _cand("n1", relevance=0.1, trust=0.4),  # low_relevance + low_trust
        _cand("n2", relevance=0.8, trust=0.4),  # low_trust
        _cand("n3", relevance=0.9, trust=0.9),  # 딱히 낮진 않지만 컷됨 → below_cut
    ]
    packet = _packet(reranked, ["r1", "r2"], {})
    assert len(packet.not_recommended) == 3
    tags = {b.block_id: b.reason_signals for b in packet.not_recommended}
    assert "low_relevance" in tags["n1"] and "low_trust" in tags["n1"]
    assert tags["n2"] == ["low_trust"]
    assert tags["n3"] == ["below_cut"]
    for block in packet.not_recommended:  # 태그 비어있지 않음
        assert block.reason_signals


# ---- 빈 추천 (경험 없음) ----

def test_empty_recommended_all_requirements_uncovered():
    packet = _packet([], [], {}, requirements=["협업", "정량성과", "대용량처리"])
    assert packet.recommended == []
    assert packet.not_recommended == []
    assert packet.uncovered_requirements == ["협업", "정량성과", "대용량처리"]
