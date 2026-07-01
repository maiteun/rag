# 시스템 구성

KHU:DArchive는 Frontend, FastAPI Backend, PostgreSQL/pgvector 저장소, AI provider 계층으로 구성됩니다.

## 전체 구조

```text
Frontend
  -> FastAPI Backend
  -> PostgreSQL / pgvector
  -> LangChain OpenAI LLM / Embeddings
```

## Backend Layer

```text
app/api          HTTP route
app/schemas      request, response, LLM schema
app/services     workflow and business logic
app/repositories database access
app/models       SQLAlchemy ORM model
app/ai           AI provider abstraction
app/utils        text and scoring utility
```

## 데이터 흐름

```text
사용자 기록 입력
  -> 원문 저장
  -> 텍스트 정제
  -> 경험 단위 구조화
  -> 출처 연결
  -> 검색 chunk 생성
  -> embedding 저장
  -> 보완 질문 생성
```

## 추천 및 초안 생성 흐름

```text
JD/문항 입력
  -> Query 분석
  -> retrieval query 생성
  -> 관련 chunk 검색
  -> experience 단위 그룹핑
  -> LLM reasoning
  -> 추천/보류/비추천 결과 생성
  -> 사용자 경험 선택
  -> 선택 경험 기준 부족 정보 및 보완 질문 생성
  -> 사용자 보완 답변 반영
  -> 선택 경험과 evidence 기반 자기소개서 초안 생성
  -> 사이트 내 수정 및 문항별 export
```

## 기술 스택

- API: FastAPI
- Data model: Pydantic v2, SQLAlchemy
- Migration: Alembic
- Database: PostgreSQL, pgvector
- AI orchestration: LangChain
- AI provider: OpenAI LLM, OpenAI Embeddings
- Local runtime: Docker Compose
- Test: pytest

## 주요 데이터

- 사용자
- 원문 문서
- 경험 카드
- 경험별 출처
- 검색 chunk
- embedding
- 보완 질문과 답변
- 추천 결과
- 사용자 선택 경험
- 자기소개서 초안 생성 요청과 응답

## 자기소개서 초안 생성 데이터 요구사항

초안 생성은 단순 생성형 답변이 아니라 경험 Vault의 구조화된 데이터를 근거로 수행합니다.

필요한 입력:

- 사용자 ID
- 지원 직무
- JD
- 자기소개서 문항
- 글자 수 또는 분량 조건
- 사용자가 선택한 경험 ID 목록
- 보완 질문 답변

필요한 출력:

- 자기소개서 초안 본문
- 사용된 경험 ID 목록
- 문항 요구사항과 연결된 근거
- 원문 evidence
- 추가 보완이 필요한 정보
- 문항별 export용 txt 또는 Markdown 본문
