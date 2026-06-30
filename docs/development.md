# Development Guide

## Requirements

- Python 3.11+
- Docker
- PostgreSQL with pgvector

## Install

```bash
cd apps/backend
python -m pip install -e ".[test]"
```

## Environment

`.env.example`을 기준으로 환경 변수를 설정합니다.

```env
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/experience_vault
LLM_PROVIDER=fake
LLM_MODEL=gpt-4.1-mini
EMBEDDING_PROVIDER=fake
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536
OPENAI_API_KEY=
```

로컬 테스트 기본값은 fake LLM/fake embedding입니다.

실제 OpenAI 연동을 사용할 때는 다음 값을 설정합니다.

```env
LLM_PROVIDER=openai
EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=...
```

LLM과 embedding 호출은 LangChain의 `langchain-openai` wrapper를 사용합니다.

## Local Database

```bash
docker compose up -d postgres
```

## Migration

```bash
cd apps/backend
alembic upgrade head
```

## Run Server

```bash
cd apps/backend
uvicorn app.main:app --reload
```

서버 실행 후 다음 경로를 사용할 수 있습니다.

- `http://localhost:8000/docs`
- `http://localhost:8000/redoc`
- `http://localhost:8000/openapi.json`

## Tests

```bash
cd apps/backend
python -m pytest -q
```

현재 테스트는 text cleaning, completeness scoring, chunk 생성, 문서 처리 파이프라인, 질문 답변 반영, retrieval 흐름을 검증합니다.

## OpenAPI Export

```bash
python scripts/export_openapi.py
```

생성 파일:

- `docs/openapi/openapi.json`
- `docs/openapi/openapi.yaml`

