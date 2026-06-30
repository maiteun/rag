from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.experience_chunk import ExperienceChunk


class ChunkRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_many(self, chunks: list[ExperienceChunk]) -> list[ExperienceChunk]:
        self.db.add_all(chunks)
        self.db.flush()
        return chunks

    def delete_by_experience(self, experience_id: str) -> None:
        self.db.execute(delete(ExperienceChunk).where(ExperienceChunk.experience_id == experience_id))
        self.db.flush()

    def list_by_user(self, user_id: str) -> list[ExperienceChunk]:
        stmt = select(ExperienceChunk).where(ExperienceChunk.user_id == user_id)
        return list(self.db.scalars(stmt).all())

