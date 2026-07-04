"""R7 컨텍스트 패킷 구성.

R3→R4가 골라낸 추천 + R1이 뽑은 요구사항을 조합해, 생성 파트(자소서 초안 LLM)에
넘길 **컨텍스트 패킷**을 만든다. 이 패킷은 생성 LLM이 "이 안의 내용만 쓰도록" 강제하는
환각 차단 장치(하드룰 3).

경계: R7은 **구조화된 신호/데이터까지만** 만든다. 자연어 이유 문장이나 완성 문단은
생성 파트 소속 → 여기서 만들지 않는다. reason_signals는 완성 문장이 아니라 태그 배열이다.
"""

from dataclasses import dataclass, field

from pydantic import BaseModel, Field

# fit 구간 경계 (조정 쉽게 상수로)
FIT_HIGH_THRESHOLD = 0.7
FIT_MID_THRESHOLD = 0.4
# not_recommended 사유 판정 임계
LOW_RELEVANCE_THRESHOLD = 0.4
LOW_TRUST_THRESHOLD = 0.5


@dataclass
class ExperienceMeta:
    """R7 입력용 경험 메타 (엔진이 Experience에서 뽑아 넘긴다)."""

    has_metric: bool = False
    has_role: bool = False
    skills: list[str] = field(default_factory=list)
    competencies: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)  # 출처 식별자/excerpt 문자열
    star_complete: bool = False  # situation/action/result 다 채워졌나


class RecommendedBlock(BaseModel):
    block_id: str
    fit: str = Field(description='"높음" | "중간" | "낮음"')
    reason_signals: list[str] = Field(description="신호 태그 배열 (문장 아님)")
    sources: list[str] = Field(default_factory=list)
    missing: list[str] = Field(default_factory=list, description="이 경험에 비어있는 정보 라벨")
    framing_hint: str | None = Field(default=None, description="풀이 순서 힌트 (규칙 기반 최소)")


class NotRecommendedBlock(BaseModel):
    block_id: str
    reason_signals: list[str] = Field(description="왜 추천 안 됐나 (태그)")


class ContextPacket(BaseModel):
    question: str
    question_type: str | None = None
    recommended: list[RecommendedBlock] = Field(default_factory=list)
    not_recommended: list[NotRecommendedBlock] = Field(default_factory=list)
    uncovered_requirements: list[str] = Field(default_factory=list)


def _norm(text: str) -> str:
    return text.strip().lower()


def _overlaps(a: str, b: str) -> bool:
    """대소문자·공백 정규화 후 문자열 키워드 매칭 (의미 매칭 아님)."""
    na, nb = _norm(a), _norm(b)
    if not na or not nb:
        return False
    return na == nb or na in nb or nb in na


def _fit(final_score: float) -> str:
    if final_score >= FIT_HIGH_THRESHOLD:
        return "높음"
    if final_score >= FIT_MID_THRESHOLD:
        return "중간"
    return "낮음"


def _reason_signals(meta: ExperienceMeta, requirements: list[str]) -> list[str]:
    signals: list[str] = []
    if meta.has_metric:
        signals.append("has_metric")
    if meta.has_role:
        signals.append("role_clear")
    for skill in meta.skills:
        if any(_overlaps(skill, req) for req in requirements):
            signals.append(f"skill_match:{skill}")
    for competency in meta.competencies:
        if any(_overlaps(competency, req) for req in requirements):
            signals.append(f"competency_match:{competency}")
    return signals


def _missing(meta: ExperienceMeta) -> list[str]:
    missing: list[str] = []
    if not meta.has_metric:
        missing.append("성과 수치 없음")
    if not meta.has_role:
        missing.append("본인 역할 불명확")
    if len(meta.sources) == 0:
        missing.append("출처 없음")
    return missing


def _not_recommended_signals(relevance: float, trust: float) -> list[str]:
    tags: list[str] = []
    if relevance < LOW_RELEVANCE_THRESHOLD:
        tags.append("low_relevance")
    if trust < LOW_TRUST_THRESHOLD:
        tags.append("low_trust")
    if not tags:  # 컷됐지만 딱히 한 신호가 낮진 않음
        tags.append("below_cut")
    return tags


def build_context_packet(
    question: str,
    question_type: str | None,
    requirements: list[str],  # R1 요구사항 키워드 (문자열). 아직 안 흐르면 []
    reranked: list,  # R3 RerankedCandidate 전체 (recommended + 나머지)
    recommended_ids: list[str],  # R4가 컷해서 남긴 block_id들
    experiences: dict,  # block_id -> ExperienceMeta
) -> ContextPacket:
    reranked_by_id = {item.block_id: item for item in reranked}
    recommended_set = set(recommended_ids)

    recommended: list[RecommendedBlock] = []
    coverage_terms: list[str] = []  # 추천 경험들이 커버하는 skill/competency 통합
    for block_id in recommended_ids:
        candidate = reranked_by_id.get(block_id)
        if candidate is None:
            continue
        meta = experiences.get(block_id) or ExperienceMeta()
        recommended.append(
            RecommendedBlock(
                block_id=block_id,
                fit=_fit(candidate.final_score),
                reason_signals=_reason_signals(meta, requirements),
                sources=list(meta.sources),
                missing=_missing(meta),
                framing_hint="문제정의 → 행동 → 결과" if meta.star_complete else None,
            )
        )
        coverage_terms.extend(meta.skills)
        coverage_terms.extend(meta.competencies)

    not_recommended = [
        NotRecommendedBlock(
            block_id=item.block_id,
            reason_signals=_not_recommended_signals(item.relevance, item.trust),
        )
        for item in reranked
        if item.block_id not in recommended_set
    ]

    # uncovered: 추천 경험들의 skill/competency에 하나도 안 잡힌 요구사항 (키워드 매칭)
    uncovered: list[str] = []
    for requirement in requirements:
        if requirement in uncovered:
            continue
        if not any(_overlaps(term, requirement) for term in coverage_terms):
            uncovered.append(requirement)

    return ContextPacket(
        question=question,
        question_type=question_type,
        recommended=recommended,
        not_recommended=not_recommended,
        uncovered_requirements=uncovered,
    )
