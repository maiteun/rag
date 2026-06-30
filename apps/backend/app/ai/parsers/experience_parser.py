import json

from app.schemas.llm import ExperienceExtractionResult


def parse_experience_json(raw: str) -> ExperienceExtractionResult:
    return ExperienceExtractionResult.model_validate(json.loads(raw))

