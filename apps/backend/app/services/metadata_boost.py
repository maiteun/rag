"""R2 ⑤ 메타데이터 소프트 부스트.

하드 필터가 아니다 — 조건이 안 맞아도 후보에서 **제외하지 않고** 점수만 가산한다.
(CLAUDE.md 원칙 5 "1차 검색은 너그럽게, 거르는 건 리랭킹에서" + 콜드스타트 이탈 방지.)

부스트 신호 2개:
- skills 겹침: 요구사항 용어(R1 skills/keywords 또는 쿼리에서 추출한 토큰)과 경험 skills의
  교집합 크기에 비례. min(겹침수, MAX_SKILL_OVERLAP)/MAX_SKILL_OVERLAP * BOOST_SKILL.
- type 맞음: 경험 experience_type이 요구사항 용어에 나타나면 BOOST_TYPE. **매핑이 본질적으로
  불확실**(JD 직무성격↔experience_type 표준 매핑 없음)해서 최소·보수적으로만 — skills가 주력.

date 신호는 **구현하지 않는다**: 빌드타임 날짜 환각 이슈(원문에 없는 날짜 채움)로 봉인.

벡터 유사도(주력, R3 w1·relevance)를 뒤엎지 않는 보조 수준으로 상수를 작게 둔다.
"""

import re

# 부스트 상수 — 작게 시작. 최대 합(BOOST_SKILL+BOOST_TYPE=0.20)이 정규화 relevance(0~1)를
# 뒤엎지 못하는 수준. 벡터 유사도가 크게 차이나면 부스트로 역전 안 됨.
BOOST_SKILL = 0.12
BOOST_TYPE = 0.08
MAX_SKILL_OVERLAP = 3  # 겹침 부스트 포화 지점 (한두 개 겹침에 과하게 쏠리지 않게)

# 라틴/숫자 런과 한글 런을 따로 끊는다 → "FastAPI로" → {"fastapi","로"} 로 스킬 토큰 보존.
_TOKEN_RE = re.compile(r"[a-z0-9]+|[가-힣]+")


def _normalize(text: str) -> str:
    return text.strip().lower()


def extract_query_terms(texts: list[str]) -> set[str]:
    """자유 텍스트(문항+JD)에서 매칭용 토큰 집합을 뽑는다 (소문자·구두점 제거).

    R1 요구사항 skills가 없을 때의 폴백. 단일어 스킬(FastAPI, PostgreSQL, Python)은
    잘 잡히고, 다어절 스킬은 놓칠 수 있음(MVP 허용 범위).
    """
    terms: set[str] = set()
    for text in texts:
        if not text:
            continue
        terms.update(_TOKEN_RE.findall(text.lower()))
    return terms


def compute_metadata_boost(
    experience_skills: list[str] | None,
    experience_type: str | None,
    requirement_terms: set[str] | list[str] | None,
) -> tuple[float, list[str]]:
    """(부스트 점수, 디버그 신호 태그) 반환. 매칭 없으면 (0.0, []) — 후보 제외는 하지 않음.

    requirement_terms: 요구사항 용어(R1 skills/keywords 또는 extract_query_terms 결과).
    대소문자·공백 정규화 후 집합 교집합으로 비교.
    """
    req = {_normalize(term) for term in (requirement_terms or []) if term and term.strip()}
    if not req:
        return 0.0, []

    skills = {_normalize(skill) for skill in (experience_skills or []) if skill and skill.strip()}
    overlap = sorted(skills & req)
    skill_boost = min(len(overlap), MAX_SKILL_OVERLAP) / MAX_SKILL_OVERLAP * BOOST_SKILL

    type_boost = 0.0
    normalized_type = _normalize(experience_type) if experience_type else ""
    if normalized_type and normalized_type in req:
        type_boost = BOOST_TYPE

    signals = [f"skill_boost:{skill}" for skill in overlap]
    if type_boost:
        signals.append(f"type_boost:{normalized_type}")
    return skill_boost + type_boost, signals
