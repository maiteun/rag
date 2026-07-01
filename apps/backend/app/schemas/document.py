from pydantic import BaseModel, Field

from app.schemas.experience import ExperienceProcessingSummary


VALID_SOURCE_TYPES = {
    "plain_text",
    "resume",
    "cover_letter",
    "portfolio",
    "memo",
    "markdown",
    "notion",
    "pdf",
}


class TextDocumentCreateRequest(BaseModel):
    user_id: str
    source_type: str
    title: str | None = None
    text: str = Field(min_length=1)
    metadata: dict = Field(default_factory=dict)


class TextDocumentCreateResponse(BaseModel):
    document_id: str
    status: str


class PdfDocumentCreateResponse(BaseModel):
    document_id: str
    status: str
    experience_count: int = 0
    question_count: int = 0
    experiences: list[ExperienceProcessingSummary] = Field(default_factory=list)


class DocumentProcessResponse(BaseModel):
    document_id: str
    status: str
    experience_count: int
    question_count: int


class DocumentProcessingResultResponse(BaseModel):
    document_id: str
    status: str
    experiences: list[ExperienceProcessingSummary]
