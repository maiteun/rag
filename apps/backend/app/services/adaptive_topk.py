"""R4 적응형 top-k.

파이프라인 위치: R2(하이브리드 검색) → R3(리랭킹) → **R4**.
R4는 R3 리랭킹 후 점수 리스트를 받아 "최종 몇 개를 추천/노출할지"(k)를 정한다.
R2의 후보 풀 크기(예: 20)와는 별개 파라미터다 — R4는 그 뒤에 붙는 최종 추천 개수 컷이다.

컷 규칙 (largest-gap + 상대 바닥 + flat 폴백):
  1. 항상 s[0] 포함 (k_min 보장).
  2. 상대 바닥: s[i] >= alpha·s[0] 인 것만 후보 (스케일 불변 → 리랭크 점수 범위가 바뀌어도 안 깨짐).
  3. 최대 gap: 인접 점수 차가 가장 큰 지점 = "적합/부적합 절벽"에서 컷.
  4. 2·3 중 더 타이트한(작은) 쪽 채택.
  5. flat 폴백: 최대 gap이 무시할 수준(< eps·s[0])이면 리랭커가 후보를 구별 못 하는 것 →
     사람이 고르도록 k_max까지 노출 (R5 선택 이벤트가 이 판단을 받아준다).
  6. [k_min, k_max] clamp.

CLAUDE.md 원칙 5("1차 검색은 너그럽게, 거르는 건 뒤에서")를 구현하는 첫 게이트.
파라미터는 alpha, flat_eps 둘뿐이라 나중에 골드셋으로 sweep 가능.
"""

from dataclasses import dataclass


@dataclass
class TopKDecision:
    k: int  # 최종 추천 개수
    rule: str  # 결정 근거: "gap"|"relative_floor"|"flat_max"|"min_guard"|"max_guard"|"empty"
    cut_score: float | None  # 컷 경계 점수 (정렬된 점수의 k-1 인덱스, 로그용)


def select_top_k(
    scores: list[float],  # R3 리랭킹 후 점수 (정렬 안 돼 있을 수 있음 → 내부에서 내림차순 정렬)
    k_min: int = 1,
    k_max: int = 5,
    alpha: float = 0.5,  # 상대 바닥 비율
    flat_eps: float = 0.05,  # flat 판정 임계 (top 대비 최대 gap 비율)
) -> TopKDecision:
    # gap/floor는 전체 후보 기준으로 산출하고 k_max는 마지막 clamp로만 적용 — 상한 초과 고득점 후보를 max_guard로 로깅하기 위함.
    n = len(scores)
    if n == 0:
        return TopKDecision(k=0, rule="empty", cut_score=None)

    ordered = sorted(scores, reverse=True)

    # 후보가 k_min 이하면 판단할 게 없다 → 있는 만큼 전부 노출.
    if n <= k_min:
        return TopKDecision(k=n, rule="min_guard", cut_score=ordered[n - 1])

    top = ordered[0]

    # 상대 바닥: s[0]은 항상 포함, 그 외 alpha·top 이상인 것만 후보로 인정.
    floor_k = max(1, sum(1 for score in ordered if score >= alpha * top))

    # 최대 gap: 인접 차가 최대인 지점에서 자른다. 동점이면 더 앞쪽(더 타이트한 컷) 선택.
    max_gap = -1.0
    gap_index = 0
    for i in range(n - 1):
        gap = ordered[i] - ordered[i + 1]
        if gap > max_gap:
            max_gap = gap
            gap_index = i
    gap_k = gap_index + 1

    # flat 폴백: 리랭커가 후보를 구별 못 함 → 최대 노출로 사람 판단에 넘긴다.
    if max_gap < flat_eps * top:
        k = min(k_max, n)
        return TopKDecision(k=k, rule="flat_max", cut_score=ordered[k - 1])

    # 상대바닥·최대gap 중 더 타이트한 쪽 채택 (동점이면 gap 우선 = 절벽 신호 우대).
    if gap_k <= floor_k:
        k, rule = gap_k, "gap"
    else:
        k, rule = floor_k, "relative_floor"

    # 가드 clamp — 걸리면 근거를 guard 규칙으로 덮어쓴다.
    if k < k_min:
        k, rule = k_min, "min_guard"
    elif k > k_max:
        k, rule = k_max, "max_guard"

    return TopKDecision(k=k, rule=rule, cut_score=ordered[k - 1])
