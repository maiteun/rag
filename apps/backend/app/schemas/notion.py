from pydantic import BaseModel, Field

from app.schemas.experience import ExperienceProcessingSummary


class NotionWorkspaceImportRequest(BaseModel):
    user_id: str
    notion_token: str | None = Field(default=None, description="Optional Notion integration token.")
    root_page_id: str | None = Field(
        default=None,
        description="Optional page id to import. If omitted, all accessible pages are discovered through search.",
    )
    workspace_name: str | None = None
    process_documents: bool = True
    max_pages: int = Field(default=100, ge=1, le=500)


class NotionImportedDocumentSummary(BaseModel):
    document_id: str
    notion_page_id: str
    title: str | None = None
    url: str | None = None
    status: str
    experience_count: int = 0
    question_count: int = 0
    experiences: list[ExperienceProcessingSummary] = Field(default_factory=list)


class NotionWorkspaceImportResponse(BaseModel):
    imported_page_count: int
    processed_document_count: int
    experience_count: int
    question_count: int
    documents: list[NotionImportedDocumentSummary]
