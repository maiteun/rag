from typing import Literal

from pydantic import BaseModel, Field


ExperienceUpdateField = Literal[
    "title",
    "summary",
    "start_date",
    "end_date",
    "experience_type",
    "organization",
    "role",
    "situation",
    "task",
    "action",
    "result",
    "learned",
    "skills",
    "competencies",
    "keywords",
]


class ExperienceFieldUpdate(BaseModel):
    field: ExperienceUpdateField
    value: str | list[str] | None = None
    mode: Literal["replace", "append"] = "replace"
    rationale: str | None = None


class ExperienceAnswerUpdateDecision(BaseModel):
    updates: list[ExperienceFieldUpdate] = Field(default_factory=list)
