from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.codes import ErrorCode
from app.core.errors import BusinessError
from app.models.match_request import MatchQuestion, MatchRequest
from app.models.user import User
from app.repositories.match_repository import MatchRepository
from app.schemas.match import (
    MatchCreateRequest,
    MatchDetailResponse,
    MatchQuestionResult,
    MatchRecommendation,
)
from app.services.recommendation_engine import RagRecommendationEngine, RecommendationEngine


class MatchService:
    def __init__(self, db: Session, engine: RecommendationEngine | None = None):
        self.db = db
        self.matches = MatchRepository(db)
        self.engine = engine or RagRecommendationEngine(db)

    def create(self, request: MatchCreateRequest) -> MatchRequest:
        self._ensure_user(request.user_id)
        match_request = MatchRequest(
            id=str(uuid4()),
            user_id=request.user_id,
            job_description=request.job_description,
            status="processing",
            questions=[
                MatchQuestion(id=str(uuid4()), position=index, text=text)
                for index, text in enumerate(request.questions)
            ],
        )
        self.matches.create(match_request)

        try:
            for question in match_request.questions:
                recommendations = self.engine.recommend(
                    request.user_id, request.job_description, question.text
                )
                self.matches.save_recommendations(
                    question, [item.model_dump() for item in recommendations]
                )
            self.matches.update_status(match_request, "completed")
        except Exception:
            self.matches.update_status(match_request, "failed")
            self.db.commit()
            raise
        self.db.commit()
        return match_request

    def get(self, match_request_id: str) -> MatchDetailResponse:
        match_request = self.matches.get(match_request_id)
        if match_request is None:
            raise BusinessError(ErrorCode.MATCH_NOT_FOUND)
        return MatchDetailResponse(
            id=match_request.id,
            status=match_request.status,
            job_description=match_request.job_description,
            questions=[
                MatchQuestionResult(
                    id=question.id,
                    text=question.text,
                    recommendations=[
                        MatchRecommendation.model_validate(item) for item in question.recommendations
                    ],
                )
                for question in match_request.questions
            ],
            created_at=match_request.created_at,
        )

    def _ensure_user(self, user_id: str) -> None:
        if self.db.get(User, user_id) is None:
            self.db.add(User(id=user_id))
            self.db.flush()
