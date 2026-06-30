from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, ForeignKey, JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class Experience(TimestampMixin, Base):
    __tablename__ = "experiences"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    experience_type: Mapped[str | None] = mapped_column(String(50))
    organization: Mapped[str | None] = mapped_column(String(255))
    role: Mapped[str | None] = mapped_column(String(255))
    situation: Mapped[str | None] = mapped_column(Text)
    task: Mapped[str | None] = mapped_column(Text)
    action: Mapped[str | None] = mapped_column(Text)
    result: Mapped[str | None] = mapped_column(Text)
    learned: Mapped[str | None] = mapped_column(Text)
    skills: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    competencies: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    keywords: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    has_metric: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_role: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_result: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_conflict: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_learning: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    completeness_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0, nullable=False)
    confidence_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="draft", nullable=False, index=True)

    user = relationship("User", back_populates="experiences")
    sources = relationship("ExperienceSource", back_populates="experience", cascade="all, delete-orphan")
    chunks = relationship("ExperienceChunk", back_populates="experience", cascade="all, delete-orphan")
    questions = relationship("ExperienceQuestion", back_populates="experience", cascade="all, delete-orphan")

