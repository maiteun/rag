from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ExperienceSource(Base):
    __tablename__ = "experience_sources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    experience_id: Mapped[str] = mapped_column(String(36), ForeignKey("experiences.id"), nullable=False, index=True)
    source_document_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("source_documents.id"),
        nullable=False,
        index=True,
    )
    source_span_start: Mapped[int | None] = mapped_column(Integer)
    source_span_end: Mapped[int | None] = mapped_column(Integer)
    source_excerpt: Mapped[str | None] = mapped_column(Text)
    extraction_confidence: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))

    experience = relationship("Experience", back_populates="sources")
    source_document = relationship("SourceDocument", back_populates="experiences")

