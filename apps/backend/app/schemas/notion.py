from pydantic import BaseModel, Field

from app.schemas.experience import ExperienceProcessingSummary


class NotionWorkspaceImportRequest(BaseModel):
    user_id: str = Field(
        description="사용자 ID (UUID). 가져온 페이지가 이 사용자의 문서로 저장됩니다.",
        examples=["00000000-0000-0000-0000-000000000001"],
    )
    notion_token: str | None = Field(
        default=None,
        description="Notion integration token. 비우면 서버의 NOTION_API_TOKEN 환경 변수를 사용합니다.",
        examples=["ntn_xxxxxxxxxxxx"],
    )
    root_page_id: str | None = Field(
        default=None,
        description="가져올 페이지 ID. 비우면 접근 가능한 모든 페이지를 검색해서 가져옵니다.",
    )
    workspace_name: str | None = Field(default=None, description="워크스페이스 이름. 문서 부가 정보에 기록됩니다.")
    process_documents: bool = Field(
        default=True, description="true면 가져온 직후 경험 추출까지 실행합니다."
    )
    max_pages: int = Field(
        default=100, ge=1, le=500, description="가져올 최대 페이지 수. 기본 100, 최대 500.", examples=[100]
    )


class NotionImportedDocumentSummary(BaseModel):
    document_id: str = Field(description="생성된 문서 ID")
    notion_page_id: str = Field(description="원본 Notion 페이지 ID")
    title: str | None = Field(default=None, description="페이지 제목")
    url: str | None = Field(default=None, description="페이지 URL")
    status: str = Field(description="문서 상태 (uploaded, processed, failed)")
    experience_count: int = Field(default=0, description="추출된 경험 수")
    question_count: int = Field(default=0, description="생성된 보완 질문 수")
    experiences: list[ExperienceProcessingSummary] = Field(
        default_factory=list, description="추출된 경험 요약 목록"
    )


class NotionWorkspaceImportResponse(BaseModel):
    imported_page_count: int = Field(description="가져온 페이지 수")
    processed_document_count: int = Field(description="경험 추출까지 마친 문서 수")
    experience_count: int = Field(description="추출된 경험 수 합계")
    question_count: int = Field(description="생성된 보완 질문 수 합계")
    documents: list[NotionImportedDocumentSummary] = Field(description="가져온 문서별 결과")
