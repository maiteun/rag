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
    user_id: str = Field(
        description="사용자 ID (UUID). 없는 사용자면 자동으로 만들어집니다.",
        examples=["00000000-0000-0000-0000-000000000001"],
    )
    source_type: str = Field(
        description="기록 종류. plain_text, resume, cover_letter, portfolio, memo, markdown, notion, pdf 중 하나.",
        examples=["cover_letter"],
    )
    title: str | None = Field(
        default=None,
        description="문서 제목. 비우면 제목 없이 저장됩니다.",
        examples=["백엔드 프로젝트 자기소개서"],
    )
    text: str = Field(
        min_length=1,
        description="기록 원문. 이 텍스트에서 경험을 추출합니다.",
        examples=["FastAPI와 PostgreSQL로 추천 API를 개발해 응답 시간을 1.8초에서 0.9초로 줄였습니다."],
    )
    metadata: dict = Field(
        default_factory=dict,
        description="부가 정보. 자유 형식 JSON 객체.",
        examples=[{"company": "삼성전자"}],
    )


class TextDocumentCreateResponse(BaseModel):
    document_id: str = Field(description="생성된 문서 ID")
    status: str = Field(description="문서 상태 (uploaded, processed, failed)")


class PdfDocumentCreateResponse(BaseModel):
    document_id: str = Field(description="생성된 문서 ID")
    status: str = Field(description="문서 상태 (uploaded, processed, failed)")
    experience_count: int = Field(default=0, description="추출된 경험 수")
    question_count: int = Field(default=0, description="생성된 보완 질문 수")
    experiences: list[ExperienceProcessingSummary] = Field(
        default_factory=list, description="추출된 경험 요약 목록"
    )


class DocumentProcessResponse(BaseModel):
    document_id: str = Field(description="처리한 문서 ID")
    status: str = Field(description="문서 상태 (processed, failed)")
    experience_count: int = Field(description="추출된 경험 수")
    question_count: int = Field(description="생성된 보완 질문 수")


class DocumentProcessingResultResponse(BaseModel):
    document_id: str = Field(description="문서 ID")
    status: str = Field(description="문서 상태")
    experiences: list[ExperienceProcessingSummary] = Field(description="추출된 경험 요약 목록")
