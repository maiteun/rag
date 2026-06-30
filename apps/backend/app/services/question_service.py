from datetime import datetime, timezone

from app.models.experience_question import ExperienceQuestion
from app.schemas.llm import ExperienceDraft


class QuestionService:
    def build_questions(self, user_id: str, experience_id: str, draft: ExperienceDraft) -> list[ExperienceQuestion]:
        now = datetime.now(timezone.utc)
        return [
            ExperienceQuestion(
                id="",
                user_id=user_id,
                experience_id=experience_id,
                question=missing.question,
                question_type=missing.question_type,
                reason=missing.reason,
                priority=missing.priority,
                status="pending",
                created_at=now,
            )
            for missing in draft.missing_fields
        ]

