"""R1 쿼리 분해 LLM 클라이언트 (base + fake + openai).

기존 추출 클라이언트(experience 쪽, 다른 개발자 담당)와 분리된 RAG 전용 모듈.
provider=openai면 실제 LLM, 아니면 결정적(deterministic) fake로 동작 → 유닛테스트는 fake로 검증.
"""

from abc import ABC, abstractmethod

from app.core.config import Settings, get_settings
from app.schemas.query_decomposition import (
    QueryDecompositionRequest,
    QueryDecompositionResult,
    QuestionType,
    Requirement,
    RequirementCategory,
)


class QueryDecompositionClient(ABC):
    @abstractmethod
    def decompose(self, request: QueryDecompositionRequest) -> QueryDecompositionResult:
        raise NotImplementedError


# fake 분류/추출에 쓰는 사전 (결정적 규칙 기반)
_QUESTION_TYPE_KEYWORDS: list[tuple[QuestionType, tuple[str, ...]]] = [
    (QuestionType.collaboration, ("협업", "갈등", "팀워크", "소통", "조율", "함께")),
    (QuestionType.problem_solving, ("문제", "해결", "트러블", "장애", "개선")),
    (QuestionType.challenge, ("도전", "실패", "극복", "역경", "어려움")),
    (QuestionType.growth, ("성장", "배운", "배움", "학습", "발전")),
    (QuestionType.motivation, ("지원", "동기", "포부", "입사")),
    (QuestionType.values, ("가치관", "신념", "인성", "원칙")),
]

_TECH_TERMS = (
    "Python", "FastAPI", "PostgreSQL", "SQL", "RAG", "OpenAI", "Docker", "Kubernetes",
    "AWS", "Java", "React", "TypeScript", "Redis", "Kafka", "머신러닝", "딥러닝", "pgvector",
)
_PERSONAL_TERMS = ("협업", "소통", "책임", "성실", "리더", "적극", "커뮤니케이션", "꼼꼼", "주도")
_DELIMITERS = ["\n", ".", ",", "·", ";", "/"]


def _split_clauses(text: str) -> list[str]:
    fragments = [text]
    for delim in _DELIMITERS:
        nxt: list[str] = []
        for frag in fragments:
            nxt.extend(frag.split(delim))
        fragments = nxt
    return [clause.strip() for clause in fragments if len(clause.strip()) >= 2]


class FakeQueryDecompositionClient(QueryDecompositionClient):
    """결정적 규칙 기반 분해 — 테스트/오프라인용."""

    def decompose(self, request: QueryDecompositionRequest) -> QueryDecompositionResult:
        return QueryDecompositionResult(
            question_type=self._classify(request.question),
            requirements=self._extract_requirements(request.job_description),
        )

    @staticmethod
    def _classify(question: str) -> QuestionType:
        for question_type, keywords in _QUESTION_TYPE_KEYWORDS:
            if any(keyword in question for keyword in keywords):
                return question_type
        return QuestionType.other

    @staticmethod
    def _extract_requirements(job_description: str) -> list[Requirement]:
        requirements: list[Requirement] = []
        seen: set[str] = set()
        for clause in _split_clauses(job_description):
            if clause in seen:
                continue
            seen.add(clause)
            tech = [term for term in _TECH_TERMS if term.lower() in clause.lower()]
            personal = [term for term in _PERSONAL_TERMS if term in clause]
            if tech:
                category = RequirementCategory.technical
                keywords = tech
            elif personal:
                category = RequirementCategory.personal
                keywords = personal
            else:
                category = RequirementCategory.experience
                keywords = []
            if any(marker in clause for marker in ("필수", "must", "required")):
                importance = 3
            elif any(marker in clause for marker in ("우대", "plus", "nice")):
                importance = 1
            else:
                importance = 2
            requirements.append(
                Requirement(text=clause, keywords=keywords, importance=importance, category=category)
            )
        return requirements


class OpenAIQueryDecompositionClient(QueryDecompositionClient):
    def __init__(self, settings: Settings):
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_openai import ChatOpenAI

        self.client = ChatOpenAI(
            api_key=settings.openai_api_key,
            model=settings.llm_model,
            temperature=0,
        ).with_structured_output(QueryDecompositionResult)
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You decompose a job description and a cover-letter question for a RAG retrieval system. "
                    "Extract concrete requirements from the job description as a list; for each set text, "
                    "search keywords, importance (3=required/필수, 1=preferred/우대, else 2), and category "
                    "(technical, experience, or personal). Do NOT invent requirements not present in the text. "
                    "Classify the question into exactly one question_type: problem_solving, collaboration, "
                    "challenge, growth, motivation, values, or other when none fit.",
                ),
                ("human", "Job description:\n{job_description}\n\nQuestion:\n{question}"),
            ]
        )

    def decompose(self, request: QueryDecompositionRequest) -> QueryDecompositionResult:
        response = (self.prompt | self.client).invoke(
            {"job_description": request.job_description, "question": request.question}
        )
        if isinstance(response, QueryDecompositionResult):
            return response
        return QueryDecompositionResult.model_validate(response)


def build_query_decomposition_client(settings: Settings | None = None) -> QueryDecompositionClient:
    settings = settings or get_settings()
    if settings.llm_provider == "openai":
        return OpenAIQueryDecompositionClient(settings)
    return FakeQueryDecompositionClient()
