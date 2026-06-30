from pydantic import BaseModel, Field


class RetrievalSearchRequest(BaseModel):
    user_id: str
    queries: list[str] = Field(min_length=1)
    top_k: int = Field(default=20, ge=1, le=100)


class RetrievalChunkResponse(BaseModel):
    chunk_id: str
    experience_id: str | None = None
    source_document_id: str | None = None
    chunk_text: str
    chunk_type: str | None = None
    similarity: float
    metadata: dict = Field(default_factory=dict)


class RetrievalSearchResponse(BaseModel):
    chunks: list[RetrievalChunkResponse]

