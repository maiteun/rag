from app.models.experience import Experience
from app.models.experience_chunk import ExperienceChunk
from app.utils.text import token_count


class ChunkingService:
    def build_chunks(self, experience: Experience, source_document_id: str | None) -> list[ExperienceChunk]:
        parts = [
            ("experience_summary", self._summary_text(experience)),
            ("situation", experience.situation),
            ("action", experience.action),
            ("result", experience.result),
            ("reflection", experience.learned),
        ]
        chunks = []
        index = 0
        for chunk_type, text in parts:
            if not text:
                continue
            chunks.append(
                ExperienceChunk(
                    id="",
                    user_id=experience.user_id,
                    experience_id=experience.id,
                    source_document_id=source_document_id,
                    chunk_text=text,
                    chunk_type=chunk_type,
                    token_count=token_count(text),
                    chunk_index=index,
                    chunk_metadata={
                        "title": experience.title,
                        "skills": experience.skills or [],
                        "competencies": experience.competencies or [],
                    },
                )
            )
            index += 1
        return chunks

    @staticmethod
    def _summary_text(experience: Experience) -> str:
        skills = ", ".join(experience.skills or [])
        return "\n".join(
            part
            for part in [
                f"Experience: {experience.title}",
                f"Summary: {experience.summary}" if experience.summary else None,
                f"Role: {experience.role}" if experience.role else None,
                f"Skills: {skills}" if skills else None,
            ]
            if part
        )

