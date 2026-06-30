import hashlib
import math

from app.ai.embeddings.base import EmbeddingClient


class FakeEmbeddingClient(EmbeddingClient):
    def __init__(self, dimension: int = 1536):
        self.dimension = dimension

    def embed(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        values = []
        for index in range(self.dimension):
            byte = digest[index % len(digest)]
            values.append((byte / 255.0) - 0.5)
        norm = math.sqrt(sum(value * value for value in values)) or 1.0
        return [value / norm for value in values]

