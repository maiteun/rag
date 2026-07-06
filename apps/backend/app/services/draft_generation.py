"""자기소개서 초안 생성 (생성 파트 역할).

선택한 경험들의 구조화 내용(STAR + facet)만 근거로, 문항에 답하는 초안을 작성한다.
원문에 없는 성과·수치·경험을 지어내지 않는다(하드룰1). 사실 나열이 아니라
"~했습니다(간략 설명) → 거기서 ~을 배웠습니다(깨달음)" 흐름으로 담백하게 맺는다.

- openai provider: LLM이 선택 경험을 엮어 초안 작성.
- fake provider(테스트/오프라인): LLM 없이 경험 내용을 결정적으로 조합한 초안.
"""
from app.core.config import get_settings
from app.models.experience import Experience


def _facet_lines(experience: Experience) -> list[str]:
    lines = []
    for facet in experience.facets or []:
        cap = facet.get("capability")
        label = facet.get("label")
        if cap or label:
            lines.append(f"{cap or ''}: {label or ''}".strip(": ").strip())
    return lines


def _grounding(experience: Experience) -> str:
    parts = [
        f"경험: {experience.title}",
        f"상황: {experience.situation}" if experience.situation else "",
        f"행동: {experience.action}" if experience.action else "",
        f"결과: {experience.result}" if experience.result else "",
        f"배운 점: {experience.learned}" if experience.learned else "",
    ]
    facets = _facet_lines(experience)
    if facets:
        parts.append("강점(facet): " + " / ".join(facets[:6]))
    return "\n".join(p for p in parts if p)


def _fallback(question_text: str, experiences: list[Experience]) -> str:
    """LLM 없이 쓰는 근거 기반 초안 — 경험 내용을 그대로 조합(지어내지 않음)."""
    paragraphs = []
    for experience in experiences:
        core = experience.action or experience.situation or experience.summary or experience.title
        learned = experience.learned or experience.result or ""
        sentence = (core or "").strip()
        if learned.strip():
            sentence = f"{sentence} 이 경험을 통해 {learned.strip()}"
        if sentence:
            paragraphs.append(sentence)
    return "\n\n".join(paragraphs) or "선택한 경험을 바탕으로 초안을 작성합니다."


def generate_draft(question_text: str, experiences: list[Experience]) -> str:
    if not experiences:
        return ""
    settings = get_settings()
    if settings.llm_provider != "openai" or not settings.openai_api_key:
        return _fallback(question_text, experiences)

    try:
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_openai import ChatOpenAI
        from pydantic import BaseModel, Field

        class Draft(BaseModel):
            draft: str = Field(description="자기소개서 초안 본문 (한국어)")

        llm = ChatOpenAI(
            api_key=settings.openai_api_key, model=settings.llm_model, temperature=0.3
        ).with_structured_output(Draft)
        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "너는 자기소개서 초안을 쓴다. 주어진 '선택한 경험들'의 내용(상황/행동/결과/배움/강점 facet)만 "
             "사용하고, 원문에 없는 사실·수치·성과는 절대 지어내지 마라.\n"
             "문체 — 사실을 냅다 나열하지 말고 자소서답게: (1) 어떤 상황·계기였는지, (2) 그래서 무엇을 왜/어떻게 "
             "했는지 간략히, (3) 그 결과와 거기서 배운 점(깨달음)으로 자연스럽게 맺는다. 깨달음은 반드시 주어진 "
             "결과·배움에 근거하고, 근거가 없으면 억지 교훈을 만들지 말고 결과로 담담히 맺어라. "
             "1인칭, 문항 취지에 맞게, 담백하되 성찰이 드러나게. 여러 경험이면 문항에 맞게 자연스럽게 엮어라."),
            ("human", "[자소서 문항]\n{q}\n\n[선택한 경험들]\n{bundle}\n\n이 경험들로 문항에 답하는 초안을 써라."),
        ])
        bundle = "\n\n".join(_grounding(e) for e in experiences)
        result = (prompt | llm).invoke({"q": question_text, "bundle": bundle})
        return (result.draft or "").strip() or _fallback(question_text, experiences)
    except Exception:
        return _fallback(question_text, experiences)
