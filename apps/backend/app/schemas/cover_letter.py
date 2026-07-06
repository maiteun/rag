from pydantic import BaseModel, Field


class CoverLetterDraftRequest(BaseModel):
    user_id: str = Field(description="사용자 ID (선택한 경험의 소유자)")
    match_id: str | None = Field(default=None, description="매칭 요청 ID (선택)")
    question_id: str | None = Field(default=None, description="문항 ID (선택)")
    question_text: str = Field(description="자기소개서 문항")
    selected_experience_ids: list[str] = Field(
        default_factory=list, description="초안에 사용할 경험 ID 목록 (드래그로 선택한 것)"
    )


class CoverLetterDraftResponse(BaseModel):
    draft: str = Field(description="생성된 자기소개서 초안")
    used_experience_ids: list[str] = Field(
        default_factory=list, description="초안 작성에 실제 사용된 경험 ID"
    )
