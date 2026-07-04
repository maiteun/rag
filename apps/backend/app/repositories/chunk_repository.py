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

    def search_by_vector(
        self, user_id: str, query_embedding: list[float], top_k: int
    ) -> list[tuple[ExperienceChunk, float]]:
        """pgvector 코사인 거리(`<=>`)로 최근접 top_k 청크를 DB에서 정렬해 가져온다.

        임베딩이 없는(NULL) 청크는 비교 불가라 제외한다. 반환은 (chunk, distance) —
        distance는 코사인 거리[0,2], 유사도 = 1 - distance 는 서비스에서 계산.
        """
        distance = ExperienceChunk.embedding.cosine_distance(query_embedding)
        stmt = (
            select(ExperienceChunk, distance.label("distance"))
            .where(ExperienceChunk.user_id == user_id)
            .where(ExperienceChunk.embedding.isnot(None))
            .order_by(distance)
            .limit(top_k)
        )
        return [(chunk, float(dist)) for chunk, dist in self.db.execute(stmt).all()]

