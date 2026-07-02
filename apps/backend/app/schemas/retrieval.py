from pydantic import BaseModel, Field


class RetrievalSearchRequest(BaseModel):
    user_id: str = Field(
        description="사용자 ID (UUID). 이 사용자의 경험 청크만 검색합니다.",
        examples=["00000000-0000-0000-0000-000000000001"],
    )
    queries: list[str] = Field(
        min_length=1,
        description="검색 질의 목록. 여러 개를 넣으면 질의별 유사도 중 최댓값으로 순위를 매깁니다.",
        examples=[["문제 해결 경험", "성능 개선"]],
    )
    top_k: int = Field(
        default=20,
        ge=1,
        le=100,
        description="가져올 청크 수. 기본 20, 최대 100.",
        examples=[20],
    )


class RetrievalChunkResponse(BaseModel):
    chunk_id: str = Field(description="청크 ID")
    experience_id: str | None = Field(default=None, description="청크가 속한 경험 ID")
    source_document_id: str | None = Field(default=None, description="원본 문서 ID")
    chunk_text: str = Field(description="청크 본문")
    chunk_type: str | None = Field(default=None, description="청크 종류 (situation, task, action, result 등)")
    similarity: float = Field(description="질의와의 유사도 (0~1)")
    metadata: dict = Field(default_factory=dict, description="청크 부가 정보")


class RetrievalSearchResponse(BaseModel):
    chunks: list[RetrievalChunkResponse] = Field(description="유사도 높은 순으로 정렬된 청크 목록")
