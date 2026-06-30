from app.ai.clients.base import ExperienceLLMClient
from app.schemas.llm import (
    EvidenceDraft,
    ExperienceDraft,
    ExperienceExtractionResult,
    MissingFieldDraft,
    StarDraft,
)


class FakeExperienceLLMClient(ExperienceLLMClient):
    def extract_experiences(self, cleaned_text: str) -> ExperienceExtractionResult:
        excerpt = cleaned_text[:500]
        if not excerpt:
            return ExperienceExtractionResult(experiences=[])

        lower = cleaned_text.lower()
        skills = []
        for skill in ["Python", "FastAPI", "PostgreSQL", "SQL", "RAG", "OpenAI"]:
            if skill.lower() in lower:
                skills.append(skill)

        title = "Extracted Career Experience"
        for line in cleaned_text.splitlines():
            if line.strip():
                title = line.strip()[:80]
                break

        result = None
        if any(marker in cleaned_text for marker in ["개선", "달성", "증가", "감소", "reduced", "improved"]):
            result = excerpt

        missing = []
        if not result:
            missing.append(
                MissingFieldDraft(
                    field="result",
                    reason="The document does not include a clear outcome or metric.",
                    question="이 경험의 결과나 개선 수치를 구체적으로 알려주실 수 있나요?",
                    question_type="metric",
                    priority=1,
                )
            )
        missing.append(
            MissingFieldDraft(
                field="role",
                reason="The user's exact ownership is not explicit enough.",
                question="이 경험에서 본인이 맡은 역할과 책임 범위는 무엇이었나요?",
                question_type="role",
                priority=2,
            )
        )

        draft = ExperienceDraft(
            title=title,
            summary=excerpt,
            experience_type="project",
            role=None,
            star=StarDraft(
                situation=excerpt,
                task=None,
                action=excerpt,
                result=result,
                learned=None,
            ),
            skills=skills,
            competencies=["problem solving"],
            keywords=skills + ["career record"],
            evidence=[EvidenceDraft(excerpt=excerpt, field="summary", confidence=0.6, span_start=0, span_end=len(excerpt))],
            missing_fields=missing,
            confidence_score=60,
        )
        return ExperienceExtractionResult(experiences=[draft])

