"""R4 적응형 top-k 단위 테스트 (순수 함수 — DB/임베딩/LLM 불필요)."""

from app.services.adaptive_topk import TopKDecision, select_top_k


def test_cliff_cuts_at_gap():
    # 0.85와 0.3 사이 절벽 → 상위 2개만.
    decision = select_top_k([0.9, 0.85, 0.3, 0.2])
    assert decision.k == 2
    assert decision.cut_score == 0.85


def test_flat_high_scores_expose_max():
    # 촘촘한 고득점 → 리랭커가 구별 못 함 → k_max까지 노출.
    decision = select_top_k([0.80, 0.79, 0.78, 0.77, 0.76, 0.75])
    assert decision.k == 5
    assert decision.rule == "flat_max"


def test_identical_scores_expose_all_up_to_max():
    # 완전 동일 → flat.
    decision = select_top_k([0.5, 0.5, 0.5])
    assert decision.k == 3
    assert decision.rule == "flat_max"


def test_single_dominant_score():
    # 하나만 압도적 → top만.
    decision = select_top_k([0.9, 0.2, 0.1])
    assert decision.k == 1


def test_all_weak_keeps_only_top():
    # 전부 약하지만 gap이 flat_eps보다 큼 → 상대바닥/gap 타이트 컷 = top 하나.
    decision = select_top_k([0.10, 0.05, 0.02])
    assert decision.k == 1


def test_single_candidate_min_guard():
    decision = select_top_k([0.5])
    assert decision == TopKDecision(k=1, rule="min_guard", cut_score=0.5)


def test_empty_input():
    decision = select_top_k([])
    assert decision == TopKDecision(k=0, rule="empty", cut_score=None)


def test_many_high_scores_clamped_by_max_guard():
    # 전부 고득점(≥0.84)인데 절벽이 k_max 뒤(index 7)에 있음 →
    # 산출 k=8이 [1,5]로 clamp → max_guard.
    scores = [0.99, 0.98, 0.97, 0.96, 0.95, 0.94, 0.93, 0.92, 0.85, 0.84]
    decision = select_top_k(scores)
    assert decision.k == 5
    assert decision.rule == "max_guard"


def test_unsorted_input_is_sorted_internally():
    # 정렬 안 된 입력도 내부에서 내림차순 정렬 후 판단.
    assert select_top_k([0.3, 0.9, 0.2, 0.85]).k == 2
