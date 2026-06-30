import math

from app.ai.embeddings.base import EmbeddingClient
from app.ai.embeddings.fake_embedding import FakeEmbeddingClient
from app.ai.embeddings.openai_embedding import OpenAIEmbeddingClient
from app.core.config import Settings, get_settings


def build_embedding_client(settings: Settings | None = None) -> EmbeddingClient:
    settings = settings or get_settings()
    if settings.embedding_provider == "openai":
        return OpenAIEmbeddingClient(settings)
    return FakeEmbeddingClient(settings.embedding_dimension)


class EmbeddingService:
    def __init__(self, client: EmbeddingClient | None = None):
        self.client = client or build_embedding_client()

    def embed(self, text: str) -> list[float]:
        return self.client.embed(text)

    @staticmethod
    def cosine_similarity(left: list[float] | None, right: list[float] | None) -> float:
        if not left or not right:
            return 0.0
        size = min(len(left), len(right))
        dot = sum(left[i] * right[i] for i in range(size))
        left_norm = math.sqrt(sum(left[i] * left[i] for i in range(size))) or 1.0
        right_norm = math.sqrt(sum(right[i] * right[i] for i in range(size))) or 1.0
        return dot / (left_norm * right_norm)

