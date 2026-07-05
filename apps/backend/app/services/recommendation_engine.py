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

# 검색 질의 결합 가중치 (문항, JD). max 병합은 JD(절대 유사도가 큼)가 독식해 문항이 무시되던
# 문제 때문에, 두 임베딩을 가중 평균한 단일 벡터로 검색한다. 동등 가중이 기본 — 골든셋으로 튜닝 여지.
QUESTION_WEIGHT = 1.0
JD_WEIGHT = 1.0


def _unique_nonempty(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        if not value or not value.strip():
            continue
        normalized = value.strip()
        key = normalized.lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(normalized)
    return result


def _facet_terms_from_metadata(metadata: dict) -> list[str]:
    return _unique_nonempty(
        [
            metadata.get("facet_capability") or "",
            metadata.get("facet_theme") or "",
            metadata.get("facet_label") or "",
            *list(metadata.get("facet_details") or []),
        ]
    )


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
        # 문항·JD를 (질의, 가중치) 쌍으로. max 병합 대신 가중 결합 → 문항이 JD에 묻히지 않게.
        queries: list[str] = []
        weights: list[float] = []
        if question and question.strip():
            queries.append(question)
            weights.append(QUESTION_WEIGHT)
        if job_description and job_description.strip():
            queries.append(job_description)
            weights.append(JD_WEIGHT)
        if not queries:
            return [], [], {}

        # R2 ⑤ 메타부스트용 요구사항 용어: 쿼리에서 추출한 토큰 ∪ (있으면) R1 skills/keywords
        boost_terms = extract_query_terms(queries)
        if requirement_terms:
            boost_terms |= {term for term in requirement_terms if term and term.strip()}

        # R2: 검색 → 경험(block) 단위 집계 (경험별 최대 유사도)
        chunks = self.retrieval.search(
            RetrievalSearchRequest(
                user_id=user_id, queries=queries, query_weights=weights, top_k=CANDIDATE_POOL_SIZE
            )
        )
        best_match = {}
        for chunk in chunks:
            if not chunk.experience_id:
                continue
            prev = best_match.get(chunk.experience_id)
            if prev is None or chunk.similarity > prev[0]:
                best_match[chunk.experience_id] = (chunk.similarity, chunk)
        if not best_match:
            return [], [], {}

        # 경험 메타 로드 → R3 입력 후보 + R7용 메타 (completeness_score 0~100 → /100)
        candidates: list[RerankCandidate] = []
        meta_by_id: dict[str, ExperienceMeta] = {}
        for experience_id, (relevance, matched_chunk) in best_match.items():
            experience = self.experiences.get(experience_id)
            if experience is None:
                continue
            chunk_metadata = matched_chunk.metadata or {}
            facet_terms = _facet_terms_from_metadata(chunk_metadata)
            experience_terms = _unique_nonempty(
                [
                    *list(experience.skills or []),
                    *list(getattr(experience, "competencies", []) or []),
                    *[
                        facet.get("capability", "")
                        for facet in (getattr(experience, "facets", []) or [])
                        if isinstance(facet, dict)
                    ],
                    *facet_terms,
                ]
            )
            # R2 ⑤ 소프트 부스트 (skills/type). 매칭 없으면 0 → 후보 유지(하드 필터 아님).
            metadata_boost, metadata_signals = compute_metadata_boost(
                experience_skills=experience_terms,
                experience_type=getattr(experience, "experience_type", None),
                requirement_terms=boost_terms,
            )
            retrieval_metadata = {
                "chunk_id": matched_chunk.chunk_id,
                "chunk_type": matched_chunk.chunk_type,
                "facet_capability": chunk_metadata.get("facet_capability"),
                "facet_label": chunk_metadata.get("facet_label"),
                "facet_details": chunk_metadata.get("facet_details") or [],
            }
            candidates.append(
                RerankCandidate(
                    block_id=experience_id,
                    search_score=relevance,
                    has_metric=bool(experience.has_metric),
                    has_role=bool(experience.has_role),
                    sources_count=len(experience.sources),
                    completeness=float(experience.completeness_score) / 100.0,
                    metadata_boost=metadata_boost,
                    metadata_signals=metadata_signals,
                    retrieval_metadata=retrieval_metadata,
                )
            )
            source_excerpts = [
                source.source_excerpt or source.source_document_id for source in experience.sources
            ]
            for excerpt in chunk_metadata.get("facet_evidence") or []:
                if excerpt and excerpt not in source_excerpts:
                    source_excerpts.append(excerpt)
            meta_by_id[experience_id] = ExperienceMeta(
                has_metric=bool(experience.has_metric),
                has_role=bool(experience.has_role),
                skills=list(experience.skills or []),
                competencies=list(experience.competencies or []),
                sources=source_excerpts,
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

    @staticmethod
    def _reason(item: RerankedCandidate) -> str:
        """관찰 신호 기반의 짧은 추천 이유 (지어내는 문장이 아니라 사실 태그 조합 — 하드룰1)."""
        parts: list[str] = []
        if item.relevance >= 0.66:
            parts.append("질의 관련도 높음")
        elif item.relevance > 0.0:
            parts.append("질의와 관련")
        sig = item.signals
        if sig.get("has_metric"):
            parts.append("성과 수치 있음")
        if sig.get("has_role"):
            parts.append("본인 역할 명확")
        if sig.get("metadata_boost", 0) > 0:
            parts.append("요구 역량 일치")
        if sig.get("sources_count", 0) >= 2:
            parts.append("복수 출처 확인")
        return " · ".join(parts[:3]) or "질의와 의미적으로 관련"

    def recommend(self, user_id: str, job_description: str, question: str) -> list[MatchRecommendation]:
        reranked, recommended_ids, _ = self._run_pipeline(user_id, job_description, question)
        by_id = {item.block_id: item for item in reranked}
        return [
            MatchRecommendation(
                experience_id=block_id,
                rank=index + 1,
                score=round(by_id[block_id].final_score, 4),
                reason=self._reason(by_id[block_id]),
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
