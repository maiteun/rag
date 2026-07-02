from typing import Protocol

from app.schemas.match import MatchRecommendation


class RecommendationEngine(Protocol):
    """문항별 경험 추천 엔진 계약. 구현은 RAG 파트 담당."""

    def recommend(self, user_id: str, job_description: str, question: str) -> list[MatchRecommendation]:
        ...


class StubRecommendationEngine:
    """RAG 추천 엔진이 붙기 전까지 빈 결과를 돌려주는 기본 구현."""

    def recommend(self, user_id: str, job_description: str, question: str) -> list[MatchRecommendation]:
        return []
