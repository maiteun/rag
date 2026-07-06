"""추천 이유 생성 (생성 파트 역할).

RAG가 정리한 grounded 번들(경험 제목 + 매칭 facet + 근거 신호)을 받아, 왜 이 경험이 해당
문항·직무에 추천됐는지 한 문장으로 설명한다. 제공된 번들 안의 내용만 근거로 쓰고 지어내지 않는다.

- openai provider: LLM이 문항당 한 번 호출로 경험별 이유를 생성.
- fake provider(테스트/오프라인): LLM 없이 매칭 facet 기반의 결정적 폴백 문장.
"""
from dataclasses import dataclass, field

from app.core.config import get_settings


@dataclass
class ReasonItem:
    experience_id: str
    title: str
    capability: str | None = None      # 매칭된 facet의 역량
    label: str | None = None           # 매칭된 facet 한줄 설명 (원문 근거)
    details: list[str] = field(default_factory=list)
    signal_tags: list[str] = field(default_factory=list)  # has_metric/role 등 관찰신호


def _fallback(item: ReasonItem) -> str:
    """LLM 없이 쓰는 근거 기반 폴백 — '어떤 facet을 쓸지'를 추천(경험 자체 설명이 아님)."""
    if item.capability:
        base = f"이 경험에선 ‘{item.capability}’ 측면을 꺼내 쓰면 좋아요"
        return f"{base} — {item.label}" if item.label else base
    if item.label:
        return item.label
    if item.signal_tags:
        return " · ".join(item.signal_tags[:3])
    return "질의와 의미적으로 관련"


def generate_reasons(question: str, job_description: str, items: list[ReasonItem]) -> dict[str, str]:
    """{experience_id: reason} 반환. 실패/폴백 시에도 항상 채워서 반환한다."""
    if not items:
        return {}
    settings = get_settings()
    if settings.llm_provider != "openai" or not settings.openai_api_key:
        return {it.experience_id: _fallback(it) for it in items}

    try:
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_openai import ChatOpenAI
        from pydantic import BaseModel, Field

        class Reason(BaseModel):
            experience_id: str = Field(description="경험 id")
            reason: str = Field(description="한 문장 추천 이유 (제공된 근거만 사용)")

        class Reasons(BaseModel):
            reasons: list[Reason]

        llm = ChatOpenAI(
            api_key=settings.openai_api_key, model=settings.llm_model, temperature=0
        ).with_structured_output(Reasons)
        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "너는 자소서 코치다. 지원자는 자기 경험 내용을 이미 안다. 그러니 경험을 처음부터 다시 설명하지 말고, "
             "‘그 경험에서 어떤 강점(facet) 측면을 이 문항·직무에 꺼내 쓰면 좋은지’를 추천하라. "
             "각 경험마다: 매칭된 강점(facet)을 중심으로 ‘이 경험에선 [강점] 측면을 쓰면 좋다’는 톤으로, "
             "그 강점이 왜 이 문항에 맞는지 한국어 한 문장. "
             "★반드시 제공된 매칭 facet·근거 안의 사실만 사용하고, 원문에 없는 성과·수치·역량을 지어내지 마라.★ "
             "각 experience_id에 대해 하나씩."),
            ("human",
             "[자소서 문항]\n{q}\n\n[직무(JD) 요약]\n{jd}\n\n[경험별 매칭된 강점(facet)과 근거]\n{bundle}\n\n"
             "각 경험에서 이 문항·직무에 꺼내 쓸 강점(facet)을 한 문장씩 추천하라."),
        ])
        bundle = "\n".join(
            f"- id={it.experience_id} | 경험: {it.title} | 매칭 강점: {it.capability or '-'}"
            f" | 근거: {it.label or '-'}"
            + (f" | 세부: {'; '.join(it.details[:3])}" if it.details else "")
            for it in items
        )
        result = (prompt | llm).invoke(
            {"q": question, "jd": job_description[:1200], "bundle": bundle}
        )
        got = {r.experience_id: r.reason.strip() for r in result.reasons if r.reason and r.reason.strip()}
        # LLM이 빠뜨린 항목은 폴백으로 보강
        return {it.experience_id: got.get(it.experience_id) or _fallback(it) for it in items}
    except Exception:
        # 생성 실패가 추천 자체를 막지 않도록 폴백
        return {it.experience_id: _fallback(it) for it in items}
