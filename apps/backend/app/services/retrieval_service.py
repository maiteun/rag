from sqlalchemy.orm import Session

from app.models.experience_chunk import ExperienceChunk
from app.repositories.chunk_repository import ChunkRepository
from app.schemas.retrieval import RetrievalChunkResponse, RetrievalSearchRequest
from app.services.embedding_service import EmbeddingService


class RetrievalService:
    def __init__(self, db: Session, embeddings: EmbeddingService | None = None):
        self.chunks = ChunkRepository(db)
        self.embeddings = embeddings or EmbeddingService()

    def search(self, request: RetrievalSearchRequest) -> list[RetrievalChunkResponse]:
        """R2 벡터 검색: pgvector `<=>`(코사인 거리)로 DB에서 top_k 최근접을 뽑는다.

        질의 여러 개면 질의별 top_k를 각각 뽑아 청크별 최대 유사도로 병합(기존 계약 유지).
        similarity = 1 - cosine_distance.
        """
        query_embeddings = [self.embeddings.embed(query) for query in request.queries]
        best: dict[str, tuple[float, ExperienceChunk]] = {}
        for query_embedding in query_embeddings:
            for chunk, distance in self.chunks.search_by_vector(
                request.user_id, query_embedding, request.top_k
            ):
                similarity = 1.0 - distance
                previous = best.get(chunk.id)
                if previous is None or similarity > previous[0]:
                    best[chunk.id] = (similarity, chunk)

        ranked = sorted(best.values(), key=lambda item: item[0], reverse=True)[: request.top_k]
        return [
            RetrievalChunkResponse(
                chunk_id=chunk.id,
                experience_id=chunk.experience_id,
                source_document_id=chunk.source_document_id,
                chunk_text=chunk.chunk_text,
                chunk_type=chunk.chunk_type,
                similarity=similarity,
                metadata=chunk.chunk_metadata or {},
            )
            for similarity, chunk in ranked
        ]

