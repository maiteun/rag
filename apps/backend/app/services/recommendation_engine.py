from typing import Protocol

from sqlalchemy.orm import Session

from app.repositories.experience_repository import ExperienceRepository
from app.schemas.match import MatchRecommendation
from app.schemas.retrieval import RetrievalSearchRequest
from app.services.adaptive_topk import select_top_k
from app.services.reranking import RerankCandidate, rerank
from app.services.retrieval_service import RetrievalService

# R2 후보 풀 크기 (넓게 뽑아 recall 확보 — R4가 뒤에서 최종 개수를 줄인다)
CANDIDATE_POOL_SIZE = 20


class RecommendationEngine(Protocol):
    """문항별 경험 추천 엔진 계약. 구현은 RAG 파트 담당."""

    def recommend(self, user_id: str, job_description: str, question: str) -> list[MatchRecommendation]:
        ...


class StubRecommendationEngine:
    """RAG 추천 엔진이 붙기 전까지 빈 결과를 돌려주는 기본 구현."""

    def recommend(self, user_id: str, job_description: str, question: str) -> list[MatchRecommendation]:
        return []


class RagRecommendationEngine:
    """실제 RAG 파이프라인: R2(검색) → R3(리랭킹) → R4(적응형 top-k).

    R1(쿼리분해) 연동은 후속 — 지금은 문항+JD를 검색 쿼리로 직접 사용.
    """

    def __init__(
        self,
        db: Session,
        retrieval: RetrievalService | None = None,
        experiences: ExperienceRepository | None = None,
    ):
        self.retrieval = retrieval or RetrievalService(db)
        self.experiences = experiences or ExperienceRepository(db)

    def recommend(self, user_id: str, job_description: str, question: str) -> list[MatchRecommendation]:
        queries = [text for text in (question, job_description) if text and text.strip()]
        if not queries:
            return []

        # R2: 검색 → 청크 결과를 경험(block) 단위로 집계 (경험별 최대 유사도)
        chunks = self.retrieval.search(
            RetrievalSearchRequest(user_id=user_id, queries=queries, top_k=CANDIDATE_POOL_SIZE)
        )
        best_relevance: dict[str, float] = {}
        for chunk in chunks:
            if not chunk.experience_id:
                continue
            prev = best_relevance.get(chunk.experience_id)
            if prev is None or chunk.similarity > prev:
                best_relevance[chunk.experience_id] = chunk.similarity
        if not best_relevance:
            return []

        # 경험 메타 로드 → R3 입력 후보 구성 (completeness_score 0~100 → /100 정규화)
        candidates: list[RerankCandidate] = []
        for experience_id, relevance in best_relevance.items():
            experience = self.experiences.get(experience_id)
            if experience is None:
                continue
            candidates.append(
                RerankCandidate(
                    block_id=experience_id,
                    search_score=relevance,
                    has_metric=bool(experience.has_metric),
                    has_role=bool(experience.has_role),
                    sources_count=len(experience.sources),
                    completeness=float(experience.completeness_score) / 100.0,
                )
            )
        if not candidates:
            return []

        # R3: 리랭킹 → R4: 적응형 top-k 컷
        reranked = rerank(candidates)
        k = select_top_k([item.final_score for item in reranked]).k
        return [
            MatchRecommendation(
                experience_id=item.block_id,
                rank=index + 1,
                score=round(item.final_score, 4),
                signals=item.signals,
            )
            for index, item in enumerate(reranked[:k])
        ]
