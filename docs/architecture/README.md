# Architecture

Career Vault backend MVP는 사용자의 과거 기록을 RAG-ready 경험 vault로 변환하는 파이프라인입니다.

## Scope

현재 구현 범위는 `apps/backend`에 집중합니다.

포함 범위:

- source document 저장
- text cleaning
- LLM 기반 experience extraction
- experience/source/chunk/question 저장
- OpenAI embedding 생성
- retrieval search
- FastAPI OpenAPI export

제외 범위:

- frontend UI
- 추천 reasoning
- 자기소개서 초안 생성
- 면접 질문 생성
- 배포 자동화

## High-Level Flow

```text
text document input
  -> source_documents
  -> text cleaning
  -> LLM extraction
  -> experiences
  -> experience_sources
  -> experience_chunks
  -> embeddings
  -> experience_questions
```

## Backend Layers

```text
app/api          HTTP routes and request/response boundaries
app/schemas      Pydantic request, response, and LLM schemas
app/services     business workflow and pipeline orchestration
app/repositories database access
app/models       SQLAlchemy ORM models
app/ai           LangChain/OpenAI and fake AI clients
app/utils        scoring and text utilities
```

## AI Providers

The application keeps AI access behind interfaces.

- LLM: fake client or LangChain `ChatOpenAI`
- Embedding: fake embedding or LangChain `OpenAIEmbeddings`

The default local configuration uses fake providers so tests do not require network access or API keys.
