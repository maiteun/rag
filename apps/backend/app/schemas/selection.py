from pydantic import BaseModel, Field


class SelectionEventCreate(BaseModel):
    user_id: str = Field(
        description="사용자 ID (UUID). 없는 사용자면 자동 생성됩니다.",
        examples=["00000000-0000-0000-0000-000000000001"],
    )
    question_type: str | None = Field(default=None, description="R1이 분류한 문항 유형")
    job_description: str | None = Field(default=None, description="JD 원문 (나중에 JD별 학습용, 지금은 저장만)")
    question_text: str | None = Field(default=None, description="문항 원문")
    exposed_block_ids: list[str] = Field(default_factory=list, description="노출된 후보 block_id 배열")
    selected_block_id: str | None = Field(default=None, description="선택한 block_id (스킵 시 None)")
    rejected_block_ids: list[str] = Field(default_factory=list, description="노출됐지만 선택 안 된 것 (soft negative)")
    signals_snapshot: dict | None = Field(default=None, description="선택 시점 후보별 신호 스냅샷")


class SelectionEventCreateResponse(BaseModel):
    selection_id: str = Field(description="저장된 선택 이벤트 ID")
