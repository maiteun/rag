from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class QuestionSummary(BaseModel):
    question_id: str
    question: str
    question_type: str | None = None
    priority: int
    status: str


class ExperienceProcessingSummary(BaseModel):
    experience_id: str
    title: str
    summary: str | None = None
    completeness_score: float
    confidence_score: float
    missing_fields: list[str] = Field(default_factory=list)
    questions: list[QuestionSummary] = Field(default_factory=list)


class ExperienceListItem(ORMModel):
    id: str
    title: str
    summary: str | None = None
    experience_type: str | None = None
    skills: list[str] = Field(default_factory=list)
    competencies: list[str] = Field(default_factory=list)
    completeness_score: Decimal
    status: str
    created_at: datetime


class ExperienceListResponse(BaseModel):
    experiences: list[ExperienceListItem]


class ExperienceSourceResponse(BaseModel):
    source_document_id: str
    title: str | None = None
    excerpt: str | None = None


class ExperienceQuestionResponse(BaseModel):
    id: str
    question: str
    question_type: str | None = None
    reason: str | None = None
    priority: int
    status: str


class ExperienceFacetResponse(BaseModel):
    capability: str
    theme: str | None = None
    label: str
    situation: str | None = None
    action: str | None = None
    result: str | None = None
    details: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)


class ExperienceDetailResponse(ORMModel):
    id: str
    title: str
    summary: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    experience_type: str | None = None
    organization: str | None = None
    role: str | None = None
    situation: str | None = None
    task: str | None = None
    action: str | None = None
    result: str | None = None
    learned: str | None = None
    skills: list[str] = Field(default_factory=list)
    competencies: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    facets: list[ExperienceFacetResponse] = Field(default_factory=list)
    completeness_score: Decimal
    confidence_score: Decimal
    sources: list[ExperienceSourceResponse] = Field(default_factory=list)
    questions: list[ExperienceQuestionResponse] = Field(default_factory=list)

