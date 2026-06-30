from sqlalchemy import ForeignKey, JSON, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class ExperienceChunk(TimestampMixin, Base):
    __tablename__ = "experience_chunks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    experience_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("experiences.id"), index=True)
    source_document_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("source_documents.id"), index=True)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_type: Mapped[str | None] = mapped_column(String(50))
    token_count: Mapped[int | None] = mapped_column(Integer)
    chunk_index: Mapped[int | None] = mapped_column(Integer)
    chunk_metadata: Mapped[dict] = mapped_column("metadata", JSON, default=dict, nullable=False)
    embedding: Mapped[list | None] = mapped_column(JSON)

    experience = relationship("Experience", back_populates="chunks")
    source_document = relationship("SourceDocument", back_populates="chunks")

