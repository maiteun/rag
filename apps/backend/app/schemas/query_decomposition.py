"""R1 쿼리 분해 스키마.

파이프라인 위치: **R1** → R2(검색) → R3(리랭킹) → R4(적응형 top-k).
입력(JD + 문항)을 받아 (1) 검색·매칭에 쓸 요구사항 리스트와 (2) 문항 유형을 뽑는다.

- requirements[] → R2 검색 쿼리 + R7 uncovered_requirements 판정의 기준
- question_type → R6 문항유형별 선호신호(w4) 학습의 키

하드룰 1(과장 금지): 원문(JD/문항)에 없는 요구사항은 지어내지 않는다.
"""

from enum import Enum

from pydantic import BaseModel, Field


class QuestionType(str, Enum):
    """자소서 문항 유형 (고정 enum 6종 + fallback)."""

    problem_solving = "problem_solving"  # 문제 해결
    collaboration = "collaboration"  # 협업·갈등 조율
    challenge = "challenge"  # 도전·실패 극복
    growth = "growth"  # 성장·학습
    motivation = "motivation"  # 지원 동기·포부
    values = "values"  # 가치관·인성
    other = "other"  # fallback (위 어디에도 안 맞을 때)

    @classmethod
    def from_raw(cls, value: str | None) -> "QuestionType":
        """LLM이 내놓은 임의 문자열을 enum으로 정규화. 모르면 other로 폴백."""
        if not value:
            return cls.other
        normalized = value.strip().lower()
        for member in cls:
            if member.value == normalized:
                return member
        return cls.other


class RequirementCategory(str, Enum):
    technical = "technical"  # 기술 (언어/프레임워크/도구)
    experience = "experience"  # 경험 (프로젝트/직무 경험)
    personal = "personal"  # 인성 (협업/태도/가치)

    @classmethod
    def from_raw(cls, value: str | None) -> "RequirementCategory":
        if not value:
            return cls.experience
        normalized = value.strip().lower()
        for member in cls:
            if member.value == normalized:
                return member
        return cls.experience


class Requirement(BaseModel):
    text: str = Field(description="요구사항 한 줄 (JD/문항에서 도출)")
    keywords: list[str] = Field(default_factory=list, description="검색용 키워드")
    importance: int = Field(default=2, ge=1, le=3, description="중요도 1(우대)~3(필수)")
    category: RequirementCategory = Field(
        default=RequirementCategory.experience, description="technical/experience/personal"
    )


class QueryDecompositionRequest(BaseModel):
    job_description: str = Field(min_length=1, description="채용 공고(JD) 원문")
    question: str = Field(min_length=1, description="자기소개서 문항")


class QueryDecompositionResult(BaseModel):
    question_type: QuestionType = Field(default=QuestionType.other, description="문항 유형")
    requirements: list[Requirement] = Field(default_factory=list, description="도출된 요구사항 리스트")
