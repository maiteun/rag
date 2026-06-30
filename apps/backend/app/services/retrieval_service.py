from sqlalchemy.orm import Session

from app.repositories.chunk_repository import ChunkRepository
from app.schemas.retrieval import RetrievalChunkResponse, RetrievalSearchRequest
from app.services.embedding_service import EmbeddingService


class RetrievalService:
    def __init__(self, db: Session, embeddings: EmbeddingService | None = None):
        self.chunks = ChunkRepository(db)
        self.embeddings = embeddings or EmbeddingService()

    def search(self, request: RetrievalSearchRequest) -> list[RetrievalChunkResponse]:
        query_embeddings = [self.embeddings.embed(query) for query in request.queries]
        scored = []
        for chunk in self.chunks.list_by_user(request.user_id):
            similarity = max(
                (self.embeddings.cosine_similarity(query_embedding, chunk.embedding) for query_embedding in query_embeddings),
                default=0.0,
            )
            scored.append((similarity, chunk))
        scored.sort(key=lambda item: item[0], reverse=True)
        seen: set[str] = set()
        results = []
        for similarity, chunk in scored:
            if chunk.id in seen:
                continue
            seen.add(chunk.id)
            results.append(
                RetrievalChunkResponse(
                    chunk_id=chunk.id,
                    experience_id=chunk.experience_id,
                    source_document_id=chunk.source_document_id,
                    chunk_text=chunk.chunk_text,
                    chunk_type=chunk.chunk_type,
                    similarity=similarity,
                    metadata=chunk.chunk_metadata or {},
                )
            )
            if len(results) >= request.top_k:
                break
        return results

