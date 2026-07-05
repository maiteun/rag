from datetime import date

from pydantic import BaseModel, Field


class PeriodDraft(BaseModel):
    start_date: date | None = None
    end_date: date | None = None
    confidence: float = 0


class StarDraft(BaseModel):
    situation: str | None = Field(
        default=None,
        description="Project/activity context plus the problem, conflict, motivation, or constraint.",
    )
    task: str | None = Field(
        default=None,
        description="The user's responsibility, objective, or decision point in that context.",
    )
    action: str | None = Field(
        default=None,
        description="Concrete actions the user personally took, preserving reusable cover-letter details.",
    )
    result: str | None = Field(
        default=None,
        description="Outcome, improvement, completion, team/project effect, metric, or visible result.",
    )
    learned: str | None = Field(
        default=None,
        description="Reflection, principle, working style, or follow-up capability gained from the experience.",
    )


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


class FacetDraft(BaseModel):
    capability: str = Field(
        description="Evidence-backed capability or strength that this facet proves, suitable for JD matching.",
    )
    theme: str | None = Field(
        default=None,
        description=(
            "Display/grouping folder, not a retrieval route. Use exactly one of: 프로젝트 수행, 데이터 분석, "
            "기술 구현, 협업, 커뮤니케이션, 문제 해결, 성과, 학습. A single experience may have facets "
            "across multiple themes. Use 프로젝트 수행 for project framing, problem definition, analysis direction "
            "redesign, scope setting, hypothesis setup, planning, prioritization, and decision-making that structures "
            "how the project is carried out. Capabilities such as 주도적 문제 정의, 문제 정의 재구성, 분석 구조 설계, "
            "and 프로젝트 방향 설정 should use 프로젝트 수행, not 문제 해결. Use 문제 해결 only for resolving execution "
            "issues, blockers, errors, conflicts, or unexpected obstacles after the project direction is already set."
        ),
    )
    label: str = Field(
        description="One-line source-backed claim describing how this capability appeared in the experience.",
    )
    situation: str | None = Field(
        default=None,
        description="Original-context situation or problem. Use null when missing from the source.",
    )
    action: str | None = Field(
        default=None,
        description="Specific action, method, decision, or ownership by the user. Use null when missing.",
    )
    result: str | None = Field(
        default=None,
        description="Outcome, impact, metric, or learning from the source. Use null when missing.",
    )
    details: list[str] = Field(
        default_factory=list,
        description=(
            "Source-grounded supporting detail sentences, including reasons, methods, criteria, tools, "
            "numbers, artifacts, techniques, and sub-steps under the label."
        ),
    )
    evidence: list[str] = Field(
        default_factory=list,
        description="Verbatim source excerpts supporting this facet.",
    )


class ExperienceDraft(BaseModel):
    title: str = Field(description="Short name for the project, activity, organization, or meaningful event.")
    summary: str | None = Field(
        default=None,
        description="1-2 sentences covering the context, user's main contribution, and outcome.",
    )
    experience_type: str | None = Field(
        default=None,
        description="Experience category such as project, internship, competition, research, class, or activity.",
    )
    organization: str | None = Field(default=None, description="Organization, team, school, company, or event name.")
    role: str | None = Field(
        default=None,
        description=(
            "Short responsibility sentence. Do not use only a label; include what the user was responsible for "
            "or did in the role."
        ),
    )
    period: PeriodDraft = Field(default_factory=PeriodDraft)
    star: StarDraft = Field(default_factory=StarDraft)
    skills: list[str] = Field(
        default_factory=list,
        description="Tools, technologies, methods, and hard skills found in the source.",
    )
    competencies: list[str] = Field(
        default_factory=list,
        description="Reusable strengths such as communication, coordination, problem solving, or documentation.",
    )
    keywords: list[str] = Field(
        default_factory=list,
        description="Searchable nouns from the source context, artifacts, issue, method, and responsibility.",
    )
    facets: list[FacetDraft] = Field(
        default_factory=list,
        description="Capability-level facets used as fine-grained RAG units and archived evidence.",
    )
    evidence: list[EvidenceDraft] = Field(default_factory=list)
    missing_fields: list[MissingFieldDraft] = Field(default_factory=list)
    confidence_score: float = 0
    completeness_score: float = 0


class ExperienceExtractionResult(BaseModel):
    experiences: list[ExperienceDraft] = Field(default_factory=list)

