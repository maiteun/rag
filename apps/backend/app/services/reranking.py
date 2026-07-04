"""R3 리랭킹.

파이프라인 위치: R2(검색) → **R3(리랭킹)** → R4(적응형 top-k, adaptive_topk.select_top_k).
R3가 재정렬해 내놓은 final_score 리스트가 R4 select_top_k의 입력이 된다.

설계: "임베딩(의미 유사도) + 룰 기반 신호"의 가중합. 크로스 인코더는 지금 안 씀
(후보 수 적고 한국어 모델 리스크 → 나중에 relevance 계산부만 교체할 수 있게 구조만 열어둠).

    final_score = w1*relevance + w2*trust + w5*frequency + w4*preference

- w1 relevance : R2 검색점수를 후보집합 내 min-max 정규화 (0~1)
- w2 trust     : 규칙 기반 신뢰도. confidence_score는 추출 환각 이슈로 안 씀 → 관찰가능 플래그만
- w5 frequency : 여러 출처에서 확인된 정도(sources 수). 작게(필터버블 방지)
- w4 preference: R6 선호신호. 미구현이라 항상 0, 계수 자리만 (R6 붙으면 상향)
- w3(과거 합격신호)는 데이터가 MVP 이후라 공식에서 제외
"""

from dataclasses import dataclass, field


def _clip(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


@dataclass
class RerankCandidate:
    """R3 입력 후보: R2 검색점수 + 리랭킹에 쓰는 경험 메타.

    completeness 는 0~1 정규화된 값 (호출부가 스케일 맞춰 넘긴다 — 예: 0~100이면 /100).
    """

    block_id: str
    search_score: float  # R2 원 검색 점수 (정규화 전)
    has_metric: bool = False
    has_role: bool = False
    sources_count: int = 0
    completeness: float = 0.0  # 0~1
    preference: float = 0.0  # R6 연결 전엔 0


@dataclass
class RerankedCandidate:
    block_id: str
    final_score: float
    relevance: float
    trust: float
    frequency: float
    preference: float
    signals: dict = field(default_factory=dict)  # 디버깅용


def _trust(candidate: RerankCandidate) -> float:
    return _clip(
        0.4  # base
        + (0.20 if candidate.has_metric else 0.0)  # 성과 수치 존재
        + (0.15 if candidate.has_role else 0.0)  # 본인 역할 명확
        + (0.10 if candidate.sources_count >= 1 else 0.0)  # 출처 있음
        + (0.10 if candidate.sources_count >= 2 else 0.0)  # 중복 출처
        + 0.15 * _clip(candidate.completeness)  # 경험 완성도(0~1)
    )


def _frequency(candidate: RerankCandidate) -> float:
    return min(candidate.sources_count, 3) / 3.0  # 0~1, 상한 3개


def _normalize_relevance(scores: list[float]) -> list[float]:
    low, high = min(scores), max(scores)
    if high == low:  # 후보 1개거나 전부 동점 → 전부 1.0 (0으로 나누기 방지)
        return [1.0] * len(scores)
    span = high - low
    return [(score - low) / span for score in scores]


def rerank(
    candidates: list,  # list[RerankCandidate] (search_score + 경험 메타)
    w1: float = 1.0,  # relevance
    w2: float = 0.3,  # trust
    w5: float = 0.1,  # frequency (작게 — 필터버블 방지)
    w4: float = 0.0,  # preference (R6 미구현 → 자리만)
) -> list[RerankedCandidate]:
    if not candidates:
        return []

    relevances = _normalize_relevance([c.search_score for c in candidates])
    reranked: list[RerankedCandidate] = []
    for candidate, relevance in zip(candidates, relevances):
        trust = _trust(candidate)
        frequency = _frequency(candidate)
        preference = candidate.preference  # 현재 항상 0
        final_score = w1 * relevance + w2 * trust + w5 * frequency + w4 * preference
        reranked.append(
            RerankedCandidate(
                block_id=candidate.block_id,
                final_score=final_score,
                relevance=relevance,
                trust=trust,
                frequency=frequency,
                preference=preference,
                signals={
                    "has_metric": candidate.has_metric,
                    "has_role": candidate.has_role,
                    "sources_count": candidate.sources_count,
                    "completeness": round(_clip(candidate.completeness), 4),
                    "search_score": candidate.search_score,
                    "weights": {"w1": w1, "w2": w2, "w5": w5, "w4": w4},
                },
            )
        )

    reranked.sort(key=lambda item: item.final_score, reverse=True)
    return reranked
