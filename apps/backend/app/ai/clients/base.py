from abc import ABC, abstractmethod

from app.schemas.llm import ExperienceExtractionResult


class ExperienceLLMClient(ABC):
    @abstractmethod
    def extract_experiences(self, cleaned_text: str) -> ExperienceExtractionResult:
        raise NotImplementedError

