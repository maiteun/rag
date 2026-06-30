from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.experience import Experience
from app.models.experience_source import ExperienceSource


class ExperienceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, experience: Experience) -> Experience:
        self.db.add(experience)
        self.db.flush()
        return experience

    def create_source(self, source: ExperienceSource) -> ExperienceSource:
        self.db.add(source)
        self.db.flush()
        return source

    def list_by_user(self, user_id: str) -> list[Experience]:
        stmt = select(Experience).where(Experience.user_id == user_id).order_by(Experience.created_at.desc())
        return list(self.db.scalars(stmt).all())

    def get(self, experience_id: str) -> Experience | None:
        stmt = (
            select(Experience)
            .where(Experience.id == experience_id)
            .options(
                selectinload(Experience.sources).selectinload(ExperienceSource.source_document),
                selectinload(Experience.questions),
            )
        )
        return self.db.scalars(stmt).first()

    def list_by_document(self, document_id: str) -> list[Experience]:
        stmt = (
            select(Experience)
            .join(ExperienceSource)
            .where(ExperienceSource.source_document_id == document_id)
            .options(selectinload(Experience.questions))
        )
        return list(self.db.scalars(stmt).all())

