"""R1 쿼리 분해 서비스.

클라이언트(fake/openai)를 감싸고, 결과를 다운스트림(R2/R3/R7)이 믿고 쓸 수 있게 정규화한다.
- question_type 은 항상 유효한 enum (모르면 other)
- 요구사항 text 중복 제거
- importance 는 스키마에서 [1,3] 보장
"""

from app.ai.clients.query_decomposition_client import (
    QueryDecompositionClient,
    build_query_decomposition_client,
)
from app.schemas.query_decomposition import (
    QueryDecompositionRequest,
    QueryDecompositionResult,
    QuestionType,
)


class QueryDecompositionService:
    def __init__(self, client: QueryDecompositionClient | None = None):
        self.client = client or build_query_decomposition_client()

    def decompose(self, request: QueryDecompositionRequest) -> QueryDecompositionResult:
        result = self.client.decompose(request)
        return QueryDecompositionResult(
            question_type=QuestionType.from_raw(result.question_type),
            requirements=self._dedupe(result.requirements),
        )

    @staticmethod
    def _dedupe(requirements):
        seen: set[str] = set()
        unique = []
        for requirement in requirements:
            key = requirement.text.strip()
            if not key or key in seen:
                continue
            seen.add(key)
            unique.append(requirement)
        return unique
