import math

from sqlalchemy.orm import Session

from app.models.experience_chunk import ExperienceChunk
from app.repositories.chunk_repository import ChunkRepository
from app.schemas.retrieval import RetrievalChunkResponse, RetrievalSearchRequest
from app.services.embedding_service import EmbeddingService


def _weighted_average(vectors: list[list[float]], weights: list[float]) -> list[float]:
    """질의 임베딩들을 가중 평균해 단위벡터로 정규화. 랭킹은 w_i·sim_i 가중합과 동일.

    (모든 벡터가 단위벡터이므로 chunk·combined = Σ w_i·(chunk·v_i) = Σ w_i·sim_i.
     |combined|는 청크마다 상수라 순위에 영향 없음.)
    """
    dim = len(vectors[0])
    accumulator = [0.0] * dim
    for vector, weight in zip(vectors, weights):
        for i in range(dim):
            accumulator[i] += weight * vector[i]
    norm = math.sqrt(sum(value * value for value in accumulator)) or 1.0
    return [value / norm for value in accumulator]


class RetrievalService:
    def __init__(self, db: Session, embeddings: EmbeddingService | None = None):
        self.chunks = ChunkRepository(db)
        self.embeddings = embeddings or EmbeddingService()

    def search(self, request: RetrievalSearchRequest) -> list[RetrievalChunkResponse]:
        """R2 벡터 검색: pgvector `<=>`(코사인 거리)로 DB에서 top_k 최근접을 뽑는다.

        - query_weights가 있으면(문항·JD 결합): 질의 임베딩을 가중 평균한 단일 벡터로 검색.
          → 스케일이 다른 질의(짧은 문항 vs 긴 JD)에서 한쪽이 max로 독식하는 문제를 없앤다.
        - 없으면(질의 변형): 질의별 top_k를 뽑아 청크별 최대 유사도로 병합(기존 계약).
        similarity = 1 - cosine_distance.
        """
        query_embeddings = [self.embeddings.embed(query) for query in request.queries]
        weights = request.query_weights
        best: dict[str, tuple[float, ExperienceChunk]] = {}

        if weights and len(weights) == len(query_embeddings):
            combined = _weighted_average(query_embeddings, weights)
            for chunk, distance in self.chunks.search_by_vector(
                request.user_id, combined, request.top_k
            ):
                best[chunk.id] = (1.0 - distance, chunk)
        else:
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

