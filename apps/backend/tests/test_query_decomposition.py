"""R1 쿼리 분해 단위 테스트 (fake 클라이언트 — LLM 호출 없음)."""

import pytest

from app.ai.clients.query_decomposition_client import FakeQueryDecompositionClient
from app.schemas.query_decomposition import (
    QueryDecompositionRequest,
    QuestionType,
    RequirementCategory,
)
from app.services.query_decomposition_service import QueryDecompositionService


def decompose(jd: str, question: str):
    service = QueryDecompositionService(client=FakeQueryDecompositionClient())
    return service.decompose(QueryDecompositionRequest(job_description=jd, question=question))


# ---- question_type 분류 ----

@pytest.mark.parametrize(
    "question, expected",
    [
        ("어려운 문제를 해결한 경험을 서술하시오.", QuestionType.problem_solving),
        ("팀원과 갈등을 조율한 경험은?", QuestionType.collaboration),
        ("가장 큰 도전과 실패 극복 경험을 쓰시오.", QuestionType.challenge),
        ("본인이 가장 성장한 경험과 배운 점은?", QuestionType.growth),
        ("우리 회사에 지원한 동기와 입사 후 포부는?", QuestionType.motivation),
        ("본인의 가치관과 신념을 서술하시오.", QuestionType.values),
        ("좋아하는 색깔은 무엇인가요?", QuestionType.other),  # fallback
    ],
)
def test_question_type_classification(question, expected):
    result = decompose("백엔드 개발자 모집", question)
    assert result.question_type == expected


# ---- requirements 추출 ----

def test_requirements_extract_keywords_and_category():
    jd = "FastAPI와 PostgreSQL 실무 경험 필수. Docker 활용 능력 우대. 원활한 협업과 소통 능력."
    result = decompose(jd, "문제 해결 경험")
    by_text = {r.text: r for r in result.requirements}

    # 기술 요구사항: 필수 → importance 3, category technical, 키워드 추출
    fastapi_req = next(r for r in result.requirements if "FastAPI" in r.text)
    assert fastapi_req.category == RequirementCategory.technical
    assert fastapi_req.importance == 3
    assert "FastAPI" in fastapi_req.keywords and "PostgreSQL" in fastapi_req.keywords

    # 우대 → importance 1
    docker_req = next(r for r in result.requirements if "Docker" in r.text)
    assert docker_req.importance == 1
    assert docker_req.category == RequirementCategory.technical

    # 인성 요구사항: 협업/소통 → personal
    soft_req = next(r for r in result.requirements if "협업" in r.text)
    assert soft_req.category == RequirementCategory.personal


def test_requirements_default_importance_and_experience_category():
    result = decompose("데이터 파이프라인을 설계하고 운영한 경험", "성장 경험")
    assert len(result.requirements) == 1
    req = result.requirements[0]
    assert req.importance == 2  # 필수/우대 마커 없음
    assert req.category == RequirementCategory.experience
    assert req.keywords == []


def test_requirements_are_deduped():
    jd = "협업 능력. 협업 능력. 성실함"
    result = decompose(jd, "협업 경험")
    texts = [r.text for r in result.requirements]
    assert len(texts) == len(set(texts))  # 중복 제거됨


def test_importance_bounds_enforced_by_schema():
    from pydantic import ValidationError
    from app.schemas.query_decomposition import Requirement

    with pytest.raises(ValidationError):
        Requirement(text="x", importance=5)


# ---- QuestionType.from_raw 폴백 ----

@pytest.mark.parametrize(
    "raw, expected",
    [
        ("problem_solving", QuestionType.problem_solving),
        ("COLLABORATION", QuestionType.collaboration),
        ("  growth  ", QuestionType.growth),
        ("unknown_type", QuestionType.other),
        (None, QuestionType.other),
        ("", QuestionType.other),
    ],
)
def test_question_type_from_raw(raw, expected):
    assert QuestionType.from_raw(raw) == expected
