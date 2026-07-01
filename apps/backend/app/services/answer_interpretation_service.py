import json
import re
from datetime import date
from typing import Protocol

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.core.config import Settings, get_settings
from app.models.experience import Experience
from app.models.experience_question import ExperienceQuestion
from app.schemas.answer_update import ExperienceAnswerUpdateDecision, ExperienceFieldUpdate


class AnswerInterpretationClient(Protocol):
    def interpret(
        self,
        experience: Experience,
        question: ExperienceQuestion,
        answer: str,
    ) -> ExperienceAnswerUpdateDecision:
        ...


def build_answer_interpretation_client(settings: Settings | None = None) -> AnswerInterpretationClient:
    settings = settings or get_settings()
    if settings.llm_provider == "openai":
        return OpenAIAnswerInterpretationClient(settings)
    return FakeAnswerInterpretationClient()


class AnswerInterpretationService:
    def __init__(self, client: AnswerInterpretationClient | None = None):
        self.client = client or build_answer_interpretation_client()

    def interpret(
        self,
        experience: Experience,
        question: ExperienceQuestion,
        answer: str,
    ) -> ExperienceAnswerUpdateDecision:
        return self.client.interpret(experience, question, answer)


class OpenAIAnswerInterpretationClient:
    def __init__(self, settings: Settings):
        self.client = ChatOpenAI(
            api_key=settings.openai_api_key,
            model=settings.llm_model,
            temperature=0,
        ).with_structured_output(ExperienceAnswerUpdateDecision)
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You update a structured career experience from a follow-up answer. "
                    "Choose only the fields directly supported by the user's answer. "
                    "Use replace for corrected atomic fields such as dates, role, organization, and title. "
                    "Use append only when the answer adds narrative detail to an existing STAR field. "
                    "For dates, return ISO date strings in YYYY-MM-DD format. "
                    "Do not invent facts and return no updates when the answer is unrelated.",
                ),
                (
                    "human",
                    "Current experience JSON:\n{experience_json}\n\n"
                    "Follow-up question JSON:\n{question_json}\n\n"
                    "User answer:\n{answer}\n\n"
                    "Return the field updates to apply.",
                ),
            ]
        )

    def interpret(
        self,
        experience: Experience,
        question: ExperienceQuestion,
        answer: str,
    ) -> ExperienceAnswerUpdateDecision:
        response = (self.prompt | self.client).invoke(
            {
                "experience_json": json.dumps(_experience_payload(experience), ensure_ascii=False),
                "question_json": json.dumps(_question_payload(question), ensure_ascii=False),
                "answer": answer,
            }
        )
        if isinstance(response, ExperienceAnswerUpdateDecision):
            return response
        return ExperienceAnswerUpdateDecision.model_validate(response)


class FakeAnswerInterpretationClient:
    def interpret(
        self,
        experience: Experience,
        question: ExperienceQuestion,
        answer: str,
    ) -> ExperienceAnswerUpdateDecision:
        target = " ".join(part or "" for part in [question.question_type, question.reason, question.question]).lower()
        if "date" in target or "period" in target or "start" in target or "end" in target:
            dates = _extract_dates(answer)
            updates = []
            if dates:
                updates.append(ExperienceFieldUpdate(field="start_date", value=dates[0].isoformat()))
            if len(dates) > 1:
                updates.append(ExperienceFieldUpdate(field="end_date", value=dates[1].isoformat()))
            return ExperienceAnswerUpdateDecision(updates=updates)
        if "role" in target:
            return ExperienceAnswerUpdateDecision(
                updates=[ExperienceFieldUpdate(field="role", value=answer, mode="replace")]
            )
        if "organization" in target or "team" in target:
            return ExperienceAnswerUpdateDecision(
                updates=[ExperienceFieldUpdate(field="organization", value=answer, mode="replace")]
            )
        if "learning" in target or "learned" in target:
            return ExperienceAnswerUpdateDecision(
                updates=[ExperienceFieldUpdate(field="learned", value=answer, mode="append")]
            )
        if "metric" in target or "result" in target:
            return ExperienceAnswerUpdateDecision(
                updates=[ExperienceFieldUpdate(field="result", value=answer, mode="append")]
            )
        return ExperienceAnswerUpdateDecision(
            updates=[ExperienceFieldUpdate(field="action", value=answer, mode="append")]
        )


def _experience_payload(experience: Experience) -> dict:
    return {
        "title": experience.title,
        "summary": experience.summary,
        "start_date": experience.start_date.isoformat() if experience.start_date else None,
        "end_date": experience.end_date.isoformat() if experience.end_date else None,
        "experience_type": experience.experience_type,
        "organization": experience.organization,
        "role": experience.role,
        "situation": experience.situation,
        "task": experience.task,
        "action": experience.action,
        "result": experience.result,
        "learned": experience.learned,
        "skills": experience.skills,
        "competencies": experience.competencies,
        "keywords": experience.keywords,
    }


def _question_payload(question: ExperienceQuestion) -> dict:
    return {
        "question": question.question,
        "question_type": question.question_type,
        "reason": question.reason,
        "priority": question.priority,
    }


def _extract_dates(text: str) -> list[date]:
    dates = []
    seen = set()
    patterns = [
        re.compile(r"(?P<year>\d{4})[-./년]\s*(?P<month>\d{1,2})[-./월]\s*(?P<day>\d{1,2})"),
        re.compile(r"(?P<year>\d{4})\s*년\s*(?P<month>\d{1,2})\s*월\s*(?P<day>\d{1,2})\s*일"),
    ]
    for pattern in patterns:
        for match in pattern.finditer(text):
            parsed = date(int(match.group("year")), int(match.group("month")), int(match.group("day")))
            if parsed not in seen:
                dates.append(parsed)
                seen.add(parsed)
    return dates
