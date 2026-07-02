from sqlalchemy import ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class MatchRequest(TimestampMixin, Base):
    __tablename__ = "match_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    job_description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False, index=True)

    user = relationship("User", back_populates="match_requests")
    questions = relationship(
        "MatchQuestion",
        back_populates="match_request",
        order_by="MatchQuestion.position",
        cascade="all, delete-orphan",
    )


class MatchQuestion(TimestampMixin, Base):
    __tablename__ = "match_questions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    match_request_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("match_requests.id"), nullable=False, index=True
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    recommendations: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    match_request = relationship("MatchRequest", back_populates="questions")
