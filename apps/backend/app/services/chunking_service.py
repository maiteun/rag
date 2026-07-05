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
        base_metadata = {
            "title": experience.title,
            "skills": experience.skills or [],
            "competencies": experience.competencies or [],
        }
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
                    chunk_metadata=base_metadata,
                )
            )
            index += 1
        for facet_index, facet in enumerate(experience.facets or []):
            text = self._facet_text(facet)
            if not text:
                continue
            chunks.append(
                ExperienceChunk(
                    id="",
                    user_id=experience.user_id,
                    experience_id=experience.id,
                    source_document_id=source_document_id,
                    chunk_text=text,
                    chunk_type="facet",
                    token_count=token_count(text),
                    chunk_index=index,
                    chunk_metadata={
                        **base_metadata,
                        "facet_index": facet_index,
                        "facet_capability": facet.get("capability"),
                        "facet_theme": facet.get("theme"),
                        "facet_label": facet.get("label"),
                        "facet_details": facet.get("details") or [],
                        "facet_evidence": facet.get("evidence") or [],
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

    @staticmethod
    def _facet_text(facet: dict) -> str:
        details = ", ".join(facet.get("details") or [])
        evidence = " ".join(facet.get("evidence") or [])
        return "\n".join(
            part
            for part in [
                f"Capability: {facet.get('capability')}" if facet.get("capability") else None,
                f"Theme: {facet.get('theme')}" if facet.get("theme") else None,
                f"Label: {facet.get('label')}" if facet.get("label") else None,
                f"Situation: {facet.get('situation')}" if facet.get("situation") else None,
                f"Action: {facet.get('action')}" if facet.get("action") else None,
                f"Result: {facet.get('result')}" if facet.get("result") else None,
                f"Details: {details}" if details else None,
                f"Evidence: {evidence}" if evidence else None,
            ]
            if part
        )

