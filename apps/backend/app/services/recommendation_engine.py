from typing import Protocol

from sqlalchemy.orm import Session

from app.repositories.experience_repository import ExperienceRepository
from app.schemas.match import MatchRecommendation
from app.schemas.query_decomposition import QueryDecompositionRequest
from app.schemas.retrieval import RetrievalSearchRequest
from app.services.adaptive_topk import select_top_k
from app.services.context_packet import ContextPacket, ExperienceMeta, build_context_packet
from app.services.metadata_boost import compute_metadata_boost, extract_query_terms
from app.services.preference import W4_DEFAULT, compute_preferences_batch
from app.services.query_decomposition_service import QueryDecompositionService
from app.services.reranking import RerankCandidate, RerankedCandidate, rerank
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
    """실제 RAG 파이프라인: R2(검색) → R3(리랭킹) → R4(적응형 top-k) → R7(컨텍스트 패킷).

    recommend()의 검색 스코어링은 R1 없이 문항+JD를 직접 쿼리로 사용(R3 결정 유지).
    build_packet()만 R1(쿼리분해)을 물어 uncovered_requirements/question_type를 채운다.
    """

    def __init__(
        self,
        db: Session,
        retrieval: RetrievalService | None = None,
        experiences: ExperienceRepository | None = None,
        decomposer: QueryDecompositionService | None = None,
    ):
        self.db = db
        self.retrieval = retrieval or RetrievalService(db)
        self.experiences = experiences or ExperienceRepository(db)
        self.decomposer = decomposer or QueryDecompositionService()

    def _run_pipeline(
        self,
        user_id: str,
        job_description: str,
        question: str,
        question_type: str | None = None,
        requirement_terms: list[str] | None = None,
    ) -> tuple[list[RerankedCandidate], list[str], dict[str, ExperienceMeta]]:
        """R2→R3→R4 공통 파이프라인. (reranked 전체, R4 컷 통과 id들, block_id별 메타) 반환.

        question_type이 주어지면 R6 선호신호(preference)를 계산해 R3에 실어준다.
        requirement_terms(R1 skills/keywords)가 있으면 쿼리 추출 토큰과 합쳐 R2 ⑤ 메타부스트에 쓴다.
        """
        queries = [text for text in (question, job_description) if text and text.strip()]
        if not queries:
            return [], [], {}

        # R2 ⑤ 메타부스트용 요구사항 용어: 쿼리에서 추출한 토큰 ∪ (있으면) R1 skills/keywords
        boost_terms = extract_query_terms(queries)
        if requirement_terms:
            boost_terms |= {term for term in requirement_terms if term and term.strip()}

        # R2: 검색 → 경험(block) 단위 집계 (경험별 최대 유사도)
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
            return [], [], {}

        # 경험 메타 로드 → R3 입력 후보 + R7용 메타 (completeness_score 0~100 → /100)
        candidates: list[RerankCandidate] = []
        meta_by_id: dict[str, ExperienceMeta] = {}
        for experience_id, relevance in best_relevance.items():
            experience = self.experiences.get(experience_id)
            if experience is None:
                continue
            # R2 ⑤ 소프트 부스트 (skills/type). 매칭 없으면 0 → 후보 유지(하드 필터 아님).
            metadata_boost, _ = compute_metadata_boost(
                experience_skills=list(experience.skills or []),
                experience_type=getattr(experience, "experience_type", None),
                requirement_terms=boost_terms,
            )
            candidates.append(
                RerankCandidate(
                    block_id=experience_id,
                    search_score=relevance,
                    has_metric=bool(experience.has_metric),
                    has_role=bool(experience.has_role),
                    sources_count=len(experience.sources),
                    completeness=float(experience.completeness_score) / 100.0,
                    metadata_boost=metadata_boost,
                )
            )
            meta_by_id[experience_id] = ExperienceMeta(
                has_metric=bool(experience.has_metric),
                has_role=bool(experience.has_role),
                skills=list(experience.skills or []),
                competencies=list(experience.competencies or []),
                sources=[
                    source.source_excerpt or source.source_document_id for source in experience.sources
                ],
                star_complete=all([experience.situation, experience.action, experience.result]),
            )
        if not candidates:
            return [], [], {}

        # R6: 문항유형별 선호신호를 계산해 후보에 실어줌 (question_type 없거나 db 없으면 0 → 영향 없음)
        if question_type is not None and self.db is not None:
            preferences = compute_preferences_batch(
                self.db, user_id, question_type, [c.block_id for c in candidates]
            )
            for candidate in candidates:
                candidate.preference = preferences.get(candidate.block_id, 0.0)

        # R3: 리랭킹(preference를 w4로 반영) → R4: 적응형 top-k 컷
        reranked = rerank(candidates, w4=W4_DEFAULT)
        k = select_top_k([item.final_score for item in reranked]).k
        recommended_ids = [item.block_id for item in reranked[:k]]
        return reranked, recommended_ids, meta_by_id

    def recommend(self, user_id: str, job_description: str, question: str) -> list[MatchRecommendation]:
        reranked, recommended_ids, _ = self._run_pipeline(user_id, job_description, question)
        by_id = {item.block_id: item for item in reranked}
        return [
            MatchRecommendation(
                experience_id=block_id,
                rank=index + 1,
                score=round(by_id[block_id].final_score, 4),
                signals=by_id[block_id].signals,
            )
            for index, block_id in enumerate(recommended_ids)
        ]

    def build_packet(self, user_id: str, job_description: str, question: str) -> ContextPacket:
        """R7: R4 컷 이후 컨텍스트 패킷 구성. R1으로 요구사항·문항유형을 채운다."""
        # R1 먼저 분해 → question_type을 R6 선호계산(파이프라인)에도 넘긴다.
        decomposition = self.decomposer.decompose(
            QueryDecompositionRequest(job_description=job_description, question=question)
        )
        question_type = decomposition.question_type.value if decomposition.question_type else None
        requirements = [
            keyword
            for requirement in decomposition.requirements
            for keyword in (requirement.keywords or [requirement.text])
        ]
        reranked, recommended_ids, meta_by_id = self._run_pipeline(
            user_id, job_description, question, question_type=question_type,
            requirement_terms=requirements,
        )
        return build_context_packet(
            question=question,
            question_type=question_type,
            requirements=requirements,
            reranked=reranked,
            recommended_ids=recommended_ids,
            experiences=meta_by_id,
        )
