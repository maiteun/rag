from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class ResumeListItem(ORMModel):
    id: str = Field(description="이력서 문서 ID")
    title: str | None = Field(default=None, description="문서 제목", examples=["이력서 v2"])
    original_filename: str | None = Field(
        default=None, description="업로드한 파일 이름 (PDF 업로드인 경우)", examples=["resume.pdf"]
    )
    source_type: str = Field(description="기록 종류 (resume 또는 pdf)")
    status: str = Field(description="문서 상태 (uploaded, processed, failed)")
    created_at: datetime = Field(description="등록 시각")


class ResumeListResponse(BaseModel):
    resumes: list[ResumeListItem] = Field(default_factory=list, description="이력서 목록. 최신순으로 정렬됩니다.")


class ResumeDetailResponse(ORMModel):
    id: str = Field(description="이력서 문서 ID")
    title: str | None = Field(default=None, description="문서 제목")
    original_filename: str | None = Field(default=None, description="업로드한 파일 이름 (PDF 업로드인 경우)")
    source_type: str = Field(description="기록 종류 (resume 또는 pdf)")
    status: str = Field(description="문서 상태")
    raw_text: str | None = Field(default=None, description="이력서 원문 텍스트")
    created_at: datetime = Field(description="등록 시각")
