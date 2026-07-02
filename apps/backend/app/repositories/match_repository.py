from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.match_request import MatchQuestion, MatchRequest


class MatchRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, match_request: MatchRequest) -> MatchRequest:
        self.db.add(match_request)
        self.db.flush()
        return match_request

    def get(self, match_request_id: str) -> MatchRequest | None:
        stmt = (
            select(MatchRequest)
            .where(MatchRequest.id == match_request_id)
            .options(selectinload(MatchRequest.questions))
        )
        return self.db.scalars(stmt).first()

    def update_status(self, match_request: MatchRequest, status: str) -> MatchRequest:
        match_request.status = status
        self.db.flush()
        return match_request

    def save_recommendations(self, question: MatchQuestion, recommendations: list[dict]) -> MatchQuestion:
        question.recommendations = recommendations
        self.db.flush()
        return question
