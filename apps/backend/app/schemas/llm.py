from datetime import date

from pydantic import BaseModel, Field


class PeriodDraft(BaseModel):
    start_date: date | None = None
    end_date: date | None = None
    confidence: float = 0


class StarDraft(BaseModel):
    situation: str | None = None
    task: str | None = None
    action: str | None = None
    result: str | None = None
    learned: str | None = None


class EvidenceDraft(BaseModel):
    excerpt: str
    field: str | None = None
    confidence: float = 0
    span_start: int | None = None
    span_end: int | None = None


class MissingFieldDraft(BaseModel):
    field: str
    reason: str
    question: str
    question_type: str = "technical_detail"
    priority: int = Field(default=3, ge=1, le=5)


class ExperienceDraft(BaseModel):
    title: str
    summary: str | None = None
    experience_type: str | None = None
    organization: str | None = None
    role: str | None = None
    period: PeriodDraft = Field(default_factory=PeriodDraft)
    star: StarDraft = Field(default_factory=StarDraft)
    skills: list[str] = Field(default_factory=list)
    competencies: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    evidence: list[EvidenceDraft] = Field(default_factory=list)
    missing_fields: list[MissingFieldDraft] = Field(default_factory=list)
    confidence_score: float = 0
    completeness_score: float = 0


class ExperienceExtractionResult(BaseModel):
    experiences: list[ExperienceDraft] = Field(default_factory=list)

