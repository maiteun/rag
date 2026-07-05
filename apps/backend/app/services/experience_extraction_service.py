from app.ai.clients.base import ExperienceLLMClient
from app.ai.clients.fake_client import FakeExperienceLLMClient
from app.ai.clients.openai_client import OpenAIExperienceLLMClient
from app.core.config import Settings, get_settings
from app.schemas.llm import ExperienceExtractionResult


def max_facets_for_text_length(text: str) -> int:
    length = len(text or "")
    if length <= 500:
        return 3
    if length <= 1500:
        return 5
    if length <= 3000:
        return 8
    if length <= 5000:
        return 10
    return 15


def build_llm_client(settings: Settings | None = None) -> ExperienceLLMClient:
    settings = settings or get_settings()
    if settings.llm_provider == "openai":
        return OpenAIExperienceLLMClient(settings)
    return FakeExperienceLLMClient()


class ExperienceExtractionService:
    def __init__(self, client: ExperienceLLMClient | None = None):
        self.client = client or build_llm_client()

    def extract(self, cleaned_text: str) -> ExperienceExtractionResult:
        result = self.client.extract_experiences(cleaned_text)
        max_facets = max_facets_for_text_length(cleaned_text)
        for experience in result.experiences:
            if len(experience.facets) > max_facets:
                experience.facets = experience.facets[:max_facets]
        return result

