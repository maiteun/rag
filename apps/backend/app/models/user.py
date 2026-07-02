from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True)
    name: Mapped[str | None] = mapped_column(String(100))

    source_documents = relationship("SourceDocument", back_populates="user")
    experiences = relationship("Experience", back_populates="user")
    match_requests = relationship("MatchRequest", back_populates="user")

