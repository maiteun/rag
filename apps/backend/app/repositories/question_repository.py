from sqlalchemy.orm import Session

from app.models.experience_question import ExperienceQuestion


class QuestionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_many(self, questions: list[ExperienceQuestion]) -> list[ExperienceQuestion]:
        self.db.add_all(questions)
        self.db.flush()
        return questions

    def get(self, question_id: str) -> ExperienceQuestion | None:
        return self.db.get(ExperienceQuestion, question_id)

