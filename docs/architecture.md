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

## 추천 단계 흐름

```text
JD/문항 입력
  -> Query 분석
  -> retrieval query 생성
  -> 관련 chunk 검색
  -> experience 단위 그룹핑
  -> LLM reasoning
  -> 추천/보류/비추천 결과 생성
  -> 부족 정보 및 보완 질문 생성
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

## 저장 데이터

- 사용자
- 원문 문서
- 경험 카드
- 경험별 출처
- 검색 chunk
- embedding
- 보완 질문과 답변
