from langchain_openai import OpenAIEmbeddings

from app.ai.embeddings.base import EmbeddingClient
from app.core.config import Settings


class OpenAIEmbeddingClient(EmbeddingClient):
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = OpenAIEmbeddings(
            api_key=settings.openai_api_key,
            model=settings.embedding_model,
            dimensions=settings.embedding_dimension,
        )

    def embed(self, text: str) -> list[float]:
        return self.client.embed_query(text)
