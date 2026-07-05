# 데이터 투입 인수인계

## 원칙

원문 데이터를 PostgreSQL 테이블에 직접 넣지 않습니다. 문서 API를 사용하면 서버가 아래 데이터를 한 번에 일관된 형태로 생성합니다.

1. `source_documents`: 입력 원문과 파일 정보
2. `experiences`: 원문에서 추출한 경험
3. `experience_sources`: 경험과 원문 근거 연결
4. `experience_chunks`: RAG 검색용 청크와 임베딩
5. `experience_questions`: 부족한 정보를 보완하기 위한 질문

직접 SQL로 일부 테이블만 채우면 경험 상세, 추천, 근거 조회가 서로 맞지 않게 됩니다.

## 1. 공통 사용자 ID 결정

현재 로그인 기능이 없으므로 데이터 담당자와 프론트엔드가 같은 사용자 ID를 사용해야 합니다. 기본값은 다음과 같습니다.

```text
00000000-0000-0000-0000-000000000001
```

루트 `.env`의 `VITE_USER_ID`가 데이터 등록 요청의 `user_id`와 같아야 합니다. `VITE_USER_ID`를 바꿨다면 프론트엔드가 빌드 시 값을 포함하므로 `docker compose up --build`를 다시 실행합니다.

## 2. 추출 방식 선택

### 실제 데이터 품질로 추출

루트에서 `.env.example`을 `.env`로 복사한 뒤 다음 항목을 설정합니다.

```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-5.4-mini
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536
OPENAI_API_KEY=sk-...
VITE_USER_ID=00000000-0000-0000-0000-000000000001
```

이 모드는 문서 처리 건마다 OpenAI API 비용이 발생하고 네트워크 연결이 필요합니다.

### 연결만 확인하는 fake 모드

기본 설정인 `LLM_PROVIDER=fake`, `EMBEDDING_PROVIDER=fake`를 사용합니다. 원문 일부를 경험 필드에 넣고 결정적인 가짜 임베딩을 생성하므로 통합 테스트에는 적합하지만 실제 추출 품질을 검증하는 데이터로 사용하면 안 됩니다.

## 3. 서비스 실행

```bash
docker compose up --build -d
docker compose ps
curl http://localhost:8000/health
```

`{"message":"ok"}`가 반환되면 데이터 투입을 시작합니다. API를 직접 작성하지 않고 브라우저에서 실행하려면 `http://localhost:8000/docs`의 **Try it out** 기능을 사용합니다.

## 4. 데이터 등록

### PDF 이력서 또는 포트폴리오

PDF는 등록과 경험 추출을 한 요청에서 처리합니다.

```bash
curl -X POST http://localhost:8000/api/documents/pdf \
  -F 'user_id=00000000-0000-0000-0000-000000000001' \
  -F 'title=2026 이력서' \
  -F 'process_document=true' \
  -F 'file=@/absolute/path/to/resume.pdf;type=application/pdf'
```

스캔 이미지만 있는 PDF는 현재 OCR하지 않습니다. PDF에서 텍스트 선택이 되는지 먼저 확인해야 합니다.

### 텍스트, Markdown, 자기소개서 원문

먼저 원문을 등록합니다.

```bash
curl -X POST http://localhost:8000/api/documents/text \
  -H 'Content-Type: application/json' \
  -d '{
    "user_id": "00000000-0000-0000-0000-000000000001",
    "source_type": "resume",
    "title": "2026 이력서",
    "text": "여기에 원문을 입력합니다.",
    "metadata": {}
  }'
```

응답의 `data.document_id`를 사용해 경험 추출을 실행합니다.

```bash
curl -X POST http://localhost:8000/api/documents/DOCUMENT_ID/process
```

`source_type`은 `plain_text`, `resume`, `cover_letter`, `portfolio`, `memo`, `markdown`, `notion`, `pdf` 중 하나를 사용합니다. 프론트의 과거 이력서 목록에는 `resume`과 `pdf`만 표시됩니다.

### Notion

Notion integration이 대상 페이지에 연결되어 있어야 합니다.

```bash
curl -X POST http://localhost:8000/api/notion/workspaces/import \
  -H 'Content-Type: application/json' \
  -d '{
    "user_id": "00000000-0000-0000-0000-000000000001",
    "notion_token": "ntn_...",
    "root_page_id": "PAGE_ID",
    "process_documents": true,
    "max_pages": 100
  }'
```

토큰을 요청 본문에 넣지 않으려면 루트 `.env`의 `NOTION_API_TOKEN`에 설정하고 `notion_token`을 생략합니다.

## 5. 투입 결과 검증

```bash
USER_ID=00000000-0000-0000-0000-000000000001
curl "http://localhost:8000/api/experiences?user_id=$USER_ID"
curl "http://localhost:8000/api/resumes?user_id=$USER_ID"
```

그다음 `http://localhost:5173`을 새로고침해 같은 데이터가 표시되는지 확인합니다. 매칭 화면에서 JD와 문항을 입력해 추천 결과까지 확인합니다.

텍스트 문서의 처리 결과는 다음 API로 다시 조회할 수 있습니다.

```bash
curl http://localhost:8000/api/documents/DOCUMENT_ID/processing-result
```

## 6. 운영 주의사항

- 동일 문서를 반복 등록하거나 처리하면 경험이 중복될 수 있으므로 요청과 응답의 `document_id`를 기록합니다.
- 원문에 이름, 연락처 등 개인정보가 있다면 외부 API 전송 정책을 먼저 확인합니다.
- DB 데이터는 `infra/postgres/data`에 유지됩니다. `docker compose down`은 데이터를 보존하지만 `docker compose down -v` 또는 해당 디렉터리 삭제는 데이터 손실 가능성이 있습니다.
- `scripts/seed_demo.py`는 연결 확인용 한 건을 만드는 도구입니다. 실제 데이터 일괄 투입 도구가 아닙니다.
