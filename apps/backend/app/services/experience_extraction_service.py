from app.ai.clients.base import ExperienceLLMClient
from app.ai.clients.fake_client import FakeExperienceLLMClient
from app.ai.clients.openai_client import OpenAIExperienceLLMClient
from app.core.config import Settings, get_settings
from app.schemas.llm import ExperienceExtractionResult


def build_llm_client(settings: Settings | None = None) -> ExperienceLLMClient:
    settings = settings or get_settings()
    if settings.llm_provider == "openai":
        return OpenAIExperienceLLMClient(settings)
    return FakeExperienceLLMClient()


class ExperienceExtractionService:
    def __init__(self, client: ExperienceLLMClient | None = None):
        self.client = client or build_llm_client()

    def extract(self, cleaned_text: str) -> ExperienceExtractionResult:
        return self.client.extract_experiences(cleaned_text)

