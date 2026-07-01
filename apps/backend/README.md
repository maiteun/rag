# Backend

KHU:DArchive backend는 사용자의 문서나 텍스트 기록을 받아 경험 단위로 정리하고, RAG에서 검색할 수 있는 chunk와 embedding을 저장하며, JD/문항 기반 경험 추천과 자기소개서 초안 생성을 지원하는 FastAPI 애플리케이션입니다.

## 구현된 기능

- 텍스트 기록 입력 API
- 원본 문서 저장 및 텍스트 정제
- LLM 기반 경험 정보 추출
- 경험 카드 저장 및 원본 evidence 연결
- 경험 기반 RAG chunk 생성
- OpenAI embedding 저장
- 경험 완성도 점수 계산
- 부족한 정보를 보완하기 위한 질문 생성
- 보완 질문 답변 반영
- 답변 반영 후 chunk와 embedding 재생성
- 사용자별 경험 목록/상세 조회
- 사용자별 retrieval search
- OpenAPI export

## MVP 추가 범위

현재 MVP 범위는 경험 추천에서 끝나지 않고 자기소개서 초안 생성까지 포함합니다. 따라서 backend는 다음 흐름을 지원해야 합니다.

1. 지원 직무, JD, 자기소개서 문항 분석
2. 경험 Vault 검색 및 문항별 top-k 추천 후보 생성
3. 추천/보류/비추천 판단과 추천하지 않는 이유를 포함한 근거 생성
4. 사용자가 선택한 경험 ID 목록 수신
5. 선택 경험의 부족한 정보 판단, 보완 질문 생성과 답변 반영
6. 선택 경험, 원문 evidence, 보완 답변 기반 자기소개서 초안 생성
7. 초안에 사용된 경험, evidence, 문항별 export 데이터 반환

## 주요 API

- `GET /health`
- `POST /api/documents/text`
- `POST /api/documents/{document_id}/process`
- `GET /api/documents/{document_id}/processing-result`
- `GET /api/experiences`
- `GET /api/experiences/{experience_id}`
- `POST /api/experience-questions/{question_id}/answer`
- `POST /api/retrieval/search`

## MVP 예정 API

- `POST /api/recommendations/experiences`
- `POST /api/cover-letters/drafts`

## DB 구성

현재 DB는 PostgreSQL을 기준으로 구성되어 있고, 초기 스키마는 `alembic/versions/0001_initial_khudarchive.py`에 정의되어 있습니다. RAG 담당자가 주로 참고할 테이블은 `experience_chunks`이며, 원본 문서와 경험 카드까지 추적하려면 `source_documents`, `experiences`, `experience_sources`를 함께 보면 됩니다.

### 전체 흐름

1. 사용자가 입력한 원본 텍스트는 `source_documents`에 저장됩니다.
2. 문서 처리 시 원본 텍스트를 정제하고, LLM으로 경험 정보를 추출합니다.
3. 추출된 경험은 `experiences`에 저장됩니다.
4. 경험과 원본 문서의 evidence 관계는 `experience_sources`에 저장됩니다.
5. 경험의 summary/situation/action/result/learned를 검색용 chunk로 나누어 `experience_chunks`에 저장합니다.
6. 각 chunk의 embedding은 `experience_chunks.embedding`에 저장합니다.
7. 보완 질문 답변이 들어오면 해당 경험의 필드를 업데이트하고, 기존 chunk를 삭제한 뒤 chunk와 embedding을 다시 생성합니다.
8. JD/문항이 입력되면 경험 chunk를 검색하고 experience 단위로 묶어 추천 후보를 구성합니다.
9. 추천 후보에는 문항별 top-k 경험, 추천/보류/비추천 판단, 추천 이유, 추천하지 않는 이유 또는 주의점, 부족한 정보를 포함합니다.
10. 사용자가 선택한 경험을 기준으로 보완 질문을 생성하고 답변을 반영합니다.
11. 사용자가 선택한 경험, 원문 evidence, 보완 답변을 바탕으로 자기소개서 초안을 생성합니다.

### 테이블 설명

#### `users`

사용자 기본 정보입니다.

| 컬럼 | 설명 |
| --- | --- |
| `id` | 사용자 ID, UUID 문자열 |
| `email` | 사용자 이메일 |
| `name` | 사용자 이름 |
| `created_at`, `updated_at` | 생성/수정 시각 |

#### `source_documents`

사용자가 입력한 원본 문서 또는 텍스트를 저장합니다.

| 컬럼 | 설명 |
| --- | --- |
| `id` | 문서 ID |
| `user_id` | 문서를 등록한 사용자 ID |
| `source_type` | 입력 유형 |
| `title` | 문서 제목 |
| `original_filename` | 업로드 파일명 |
| `external_url` | 외부 URL |
| `raw_text` | 사용자가 입력한 원본 텍스트 |
| `cleaned_text` | 정제된 텍스트 |
| `status` | 처리 상태. 예: `uploaded`, `processed`, `failed` |
| `metadata` | 추가 메타데이터 또는 처리 오류 정보 |
| `created_at`, `updated_at` | 생성/수정 시각 |

#### `experiences`

LLM이 원본 문서에서 추출한 경험 카드입니다. 자기소개서나 면접 답변 생성 시 중심 데이터가 됩니다.

| 컬럼 | 설명 |
| --- | --- |
| `id` | 경험 ID |
| `user_id` | 경험 소유 사용자 ID |
| `title` | 경험 제목 |
| `summary` | 경험 요약 |
| `start_date`, `end_date` | 경험 기간 |
| `experience_type` | 경험 유형 |
| `organization` | 소속/기관 |
| `role` | 본인의 역할 |
| `situation`, `task`, `action`, `result` | STAR 구조 필드 |
| `learned` | 배운 점/회고 |
| `skills` | 관련 기술 목록, JSON 배열 |
| `competencies` | 역량 목록, JSON 배열 |
| `keywords` | 키워드 목록, JSON 배열 |
| `has_metric`, `has_role`, `has_result`, `has_conflict`, `has_learning` | 경험 완성도 판단용 플래그 |
| `completeness_score` | 경험 완성도 점수 |
| `confidence_score` | LLM 추출 신뢰도 |
| `status` | 경험 상태. 예: `draft`, `needs_review`, `confirmed` |
| `created_at`, `updated_at` | 생성/수정 시각 |

#### `experience_sources`

`experiences`와 `source_documents` 사이의 evidence 연결 테이블입니다. 어떤 원문 구간에서 경험이 추출되었는지 확인할 때 사용합니다.

| 컬럼 | 설명 |
| --- | --- |
| `id` | evidence 연결 ID |
| `experience_id` | 연결된 경험 ID |
| `source_document_id` | 연결된 원본 문서 ID |
| `source_span_start`, `source_span_end` | 원문 내 evidence 위치 |
| `source_excerpt` | evidence 원문 일부 |
| `extraction_confidence` | 해당 evidence 기반 추출 신뢰도 |

#### `experience_chunks`

RAG 검색의 핵심 테이블입니다. 검색 대상 텍스트 chunk와 embedding을 저장합니다.

| 컬럼 | 설명 |
| --- | --- |
| `id` | chunk ID |
| `user_id` | chunk 소유 사용자 ID |
| `experience_id` | chunk가 연결된 경험 ID |
| `source_document_id` | chunk가 유래한 원본 문서 ID |
| `chunk_text` | 검색에 사용할 실제 텍스트 |
| `chunk_type` | chunk 종류. 예: `experience_summary`, `situation`, `action`, `result`, `reflection` |
| `token_count` | chunk token 수 |
| `chunk_index` | 같은 경험 안에서의 chunk 순서 |
| `metadata` | 검색 결과에 함께 내려줄 메타데이터. 현재 `title`, `skills`, `competencies` 포함 |
| `embedding` | chunk embedding 배열. 현재 SQLAlchemy 모델에서는 JSON으로 저장 |
| `created_at`, `updated_at` | 생성/수정 시각 |

현재 retrieval API는 `user_id`로 `experience_chunks`를 조회한 뒤, 요청 query embedding과 `embedding`의 cosine similarity를 계산하여 유사도 순으로 `top_k`개를 반환합니다.

`POST /api/retrieval/search` 요청 예시:

```json
{
  "user_id": "user-id",
  "queries": ["문제 해결 경험", "협업 갈등 해결"],
  "top_k": 10
}
```

응답 chunk에는 `chunk_id`, `experience_id`, `source_document_id`, `chunk_text`, `chunk_type`, `similarity`, `metadata`가 포함됩니다. RAG 답변에서 원본 추적이 필요하면 `experience_id`로 `experiences`를, `source_document_id`로 `source_documents`를 추가 조회하면 됩니다.

#### `experience_questions`

추출된 경험에서 부족한 정보를 사용자에게 다시 질문하기 위한 테이블입니다.

| 컬럼 | 설명 |
| --- | --- |
| `id` | 질문 ID |
| `user_id` | 질문 대상 사용자 ID |
| `experience_id` | 질문이 연결된 경험 ID |
| `question` | 사용자에게 보여줄 질문 |
| `question_type` | 부족한 정보 유형. 예: `metric`, `result`, `learning`, `role` |
| `reason` | 질문 생성 이유 |
| `priority` | 질문 우선순위 |
| `status` | 답변 상태. 예: `pending`, `answered` |
| `answer` | 사용자 답변 |
| `created_at`, `answered_at` | 생성/답변 시각 |

#### 자기소개서 초안 생성 데이터

초안 생성 결과를 영속화할지 여부는 아직 확정되지 않았습니다. MVP에서는 최소한 API 응답으로 다음 데이터를 반환해야 합니다.

| 필드 | 설명 |
| --- | --- |
| `draft` | 생성된 자기소개서 초안 본문 |
| `used_experience_ids` | 초안에 사용된 경험 ID 목록 |
| `evidence` | 초안 생성에 사용된 원문 근거 |
| `missing_information` | 추가 보완이 필요한 정보 |
| `exports` | 문항별 txt, Markdown 등 export용 본문 |

### RAG 담당자 참고 사항

- 검색에 바로 사용할 데이터는 `experience_chunks.chunk_text`와 `experience_chunks.embedding`입니다.
- 검색 범위는 사용자별로 분리되어 있으므로 `user_id` 조건을 반드시 사용해야 합니다.
- chunk는 경험 단위로 생성되며, `experience_id`를 통해 구조화된 STAR 필드와 점수 정보를 조회할 수 있습니다.
- 원문 evidence가 필요하면 `experience_sources`를 통해 `source_documents.raw_text`, `source_documents.cleaned_text`, `source_excerpt`를 확인할 수 있습니다.
- 보완 질문 답변 후에는 기존 chunk가 재생성되므로, 같은 `experience_id`의 chunk ID는 바뀔 수 있습니다.
- 현재 migration에는 `pgvector` extension 생성과 `embedding` ivfflat index 생성 코드가 있지만, 모델 컬럼은 JSON으로 정의되어 있습니다. 실제 벡터 인덱스 기반 검색으로 전환하려면 `embedding` 컬럼 타입을 pgvector `Vector(dim)` 형태로 맞추는 작업이 필요합니다.
- 자기소개서 초안 생성 시에는 시스템 추천 결과가 아니라 사용자가 선택한 경험 ID 목록을 기준으로 해야 합니다.
- 자기소개서 초안 생성 시에도 원문에 없는 사실을 만들지 않도록 `experience_sources.source_excerpt`와 보완 답변을 함께 참조해야 합니다.

## 실행

```bash
cd apps/backend
uvicorn app.main:app --reload
```

## 테스트

```bash
cd apps/backend
python -m pytest -q
```

## 설정

환경 변수는 루트의 `.env.example`을 기준으로 설정합니다.
