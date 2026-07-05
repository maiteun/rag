# KHU:DArchive 전체 실행 및 데이터 투입 가이드

이 문서는 처음 코드베이스를 받은 사람이 로컬에서 전체 서비스를 실행하고 실제 데이터를 투입한 뒤 프론트엔드에서 확인하는 절차를 설명합니다.

## 1. 실행 구성

`docker compose up`으로 다음 서비스가 실행됩니다.

| 서비스 | 역할 | 로컬 주소 |
| --- | --- | --- |
| `postgres` | PostgreSQL 16 + pgvector | `localhost:5432` |
| `backend` | FastAPI, DB 마이그레이션, 경험 추출 및 추천 | `http://localhost:8000` |
| `frontend` | React 정적 파일과 `/api` 프록시 | `http://localhost:5173` |

서비스 시작 시 DB 테이블은 자동 생성되지만 사용자 데이터는 자동으로 들어가지 않습니다. 데이터는 5장의 문서 API를 통해 별도로 등록합니다.

## 2. 사전 준비

필수 프로그램:

- Git
- Docker Desktop 또는 Docker Engine + Compose
- 데모 스크립트를 사용할 경우 Python 3

Docker Desktop을 사용하는 환경에서는 Docker Desktop을 먼저 실행하고 엔진이 준비됐는지 확인합니다.

```bash
docker version
docker compose version
```

`docker version` 결과에 `Server` 정보가 없으면 Docker daemon이 아직 실행되지 않은 상태입니다.

## 3. 환경 변수 설정

저장소 루트에서 예제 파일을 복사합니다.

```bash
cp .env.example .env
```

### 실제 데이터를 추출하는 설정

`.env`에서 다음 값을 설정합니다.

```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-5.4-mini
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536
OPENAI_API_KEY=sk-...
NOTION_API_TOKEN=
NOTION_API_VERSION=2026-03-11
VITE_USER_ID=00000000-0000-0000-0000-000000000001
```

OpenAI 모드는 문서 처리 시 외부 API를 호출하므로 네트워크 연결과 API 사용 권한 및 비용이 필요합니다.

### 연결만 확인하는 설정

OpenAI 키 없이 실행 흐름만 확인하려면 기본 fake provider를 사용합니다.

```env
LLM_PROVIDER=fake
EMBEDDING_PROVIDER=fake
OPENAI_API_KEY=
VITE_USER_ID=00000000-0000-0000-0000-000000000001
```

fake provider는 원문 일부를 단순한 경험 구조로 변환하고 가짜 임베딩을 만듭니다. 실제 추출 품질이나 추천 품질을 평가하는 용도로 사용하면 안 됩니다.

### 사용자 ID 주의사항

현재 로그인 기능이 없으므로 `VITE_USER_ID`가 화면에 표시할 사용자를 결정합니다. 모든 데이터 등록 요청의 `user_id`를 이 값과 동일하게 사용해야 합니다.

```text
VITE_USER_ID == 데이터 등록 요청의 user_id
```

`VITE_USER_ID`를 변경했다면 프론트엔드에 다시 포함되도록 `docker compose up --build`를 실행해야 합니다.

## 4. 전체 서비스 실행

저장소 루트에서 실행합니다.

```bash
docker compose up --build -d
```

최초 실행은 이미지를 내려받고 프론트·백엔드 이미지를 빌드하므로 시간이 걸릴 수 있습니다. 상태를 확인합니다.

```bash
docker compose ps
```

`postgres`, `backend`, `frontend`가 모두 `running` 또는 `healthy` 상태여야 합니다. 로그는 다음 명령으로 확인합니다.

```bash
docker compose logs -f
```

백엔드와 프론트엔드를 확인합니다.

```bash
curl http://localhost:8000/health
curl http://localhost:5173/health
```

정상 응답:

```json
{"message":"ok"}
```

브라우저 주소:

- 서비스 화면: `http://localhost:5173`
- Swagger API 문서: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

이 시점에 화면의 경험 및 이력서 목록이 비어 있는 것은 정상입니다.

## 5. 데이터 투입

### 데이터 처리 원칙

PostgreSQL에 직접 `INSERT`하지 않습니다. 문서 API를 사용해야 서버가 다음 데이터를 함께 생성합니다.

- 원본 문서
- 구조화된 경험
- 경험과 원문의 근거 관계
- 검색용 청크와 임베딩
- 부족한 정보에 대한 보완 질문

직접 SQL로 일부 테이블만 채우면 경험 상세와 RAG 추천의 데이터 정합성이 깨질 수 있습니다.

API 명령 대신 화면에서 입력하려면 `http://localhost:8000/docs`에서 해당 API를 선택하고 **Try it out**을 사용합니다.

### 5.1 PDF 등록

PDF 등록 API는 기본적으로 텍스트 추출과 경험 생성을 한 번에 실행합니다.

```bash
curl -X POST http://localhost:8000/api/documents/pdf \
  -F 'user_id=00000000-0000-0000-0000-000000000001' \
  -F 'title=2026 이력서' \
  -F 'process_document=true' \
  -F 'file=@/absolute/path/to/resume.pdf;type=application/pdf'
```

`/absolute/path/to/resume.pdf`를 실제 PDF의 절대 경로로 바꿉니다. 현재 OCR 기능은 없으므로 스캔 이미지만 있는 PDF가 아니라 텍스트 선택이 가능한 PDF를 사용해야 합니다.

성공 응답의 주요 값:

```json
{
  "success": true,
  "data": {
    "document_id": "...",
    "status": "processed",
    "experience_count": 1
  }
}
```

PDF 문서는 프론트의 과거 이력서 목록에도 표시됩니다.

### 5.2 텍스트·Markdown·자기소개서 등록

텍스트는 등록과 처리를 두 단계로 실행합니다.

1단계: 원문 등록

```bash
curl -X POST http://localhost:8000/api/documents/text \
  -H 'Content-Type: application/json' \
  -d '{
    "user_id": "00000000-0000-0000-0000-000000000001",
    "source_type": "resume",
    "title": "2026 이력서",
    "text": "FastAPI와 PostgreSQL로 추천 API를 개발하고 응답 시간을 개선했습니다.",
    "metadata": {}
  }'
```

응답에서 `data.document_id`를 복사합니다.

2단계: 경험 추출 및 임베딩 생성

```bash
curl -X POST http://localhost:8000/api/documents/DOCUMENT_ID/process
```

`DOCUMENT_ID`를 1단계에서 받은 값으로 바꿉니다.

허용되는 `source_type`:

| 값 | 용도 |
| --- | --- |
| `resume` | 이력서. 프론트 이력서 목록에 표시 |
| `pdf` | PDF 문서 |
| `cover_letter` | 기존 자기소개서 |
| `portfolio` | 포트폴리오 |
| `memo` | 경험 메모 |
| `markdown` | Markdown 문서 |
| `notion` | Notion 원문 |
| `plain_text` | 기타 텍스트 |

프론트의 과거 이력서 목록에는 `resume`과 `pdf`만 표시되지만, 다른 유형에서 추출된 경험도 경험 목록과 추천에 사용됩니다.

### 5.3 Notion 등록

먼저 Notion integration을 만들고 읽을 페이지에 연결합니다. 토큰은 `.env`의 `NOTION_API_TOKEN`에 설정하는 방식을 권장합니다.

```env
NOTION_API_TOKEN=ntn_...
```

환경 변수를 바꿨다면 백엔드를 다시 생성합니다.

```bash
docker compose up --build -d backend frontend
```

특정 루트 페이지와 하위 페이지를 가져옵니다.

```bash
curl -X POST http://localhost:8000/api/notion/workspaces/import \
  -H 'Content-Type: application/json' \
  -d '{
    "user_id": "00000000-0000-0000-0000-000000000001",
    "root_page_id": "NOTION_PAGE_ID",
    "process_documents": true,
    "max_pages": 100
  }'
```

`root_page_id`를 생략하면 integration이 접근 가능한 페이지를 검색합니다. 데이터 범위가 예상보다 넓어질 수 있으므로 처음에는 명시하는 편이 안전합니다.

### 5.4 데모 데이터 한 건 생성

fake provider에서 통합 연결만 빠르게 확인할 때 사용합니다.

```bash
python3 scripts/seed_demo.py
```

이 스크립트는 해당 사용자의 경험이 이미 있으면 중복 생성을 건너뜁니다. 실제 데이터 일괄 투입 도구는 아닙니다.

## 6. 투입 결과 검증

공통 사용자 ID를 사용해 경험 및 이력서 목록을 조회합니다.

```bash
USER_ID=00000000-0000-0000-0000-000000000001
curl "http://localhost:8000/api/experiences?user_id=$USER_ID"
curl "http://localhost:8000/api/resumes?user_id=$USER_ID"
```

특정 문서의 처리 결과:

```bash
curl http://localhost:8000/api/documents/DOCUMENT_ID/processing-result
```

검증 순서:

1. 경험 목록 응답의 `data.experiences`가 비어 있지 않은지 확인합니다.
2. 이력서를 넣었다면 이력서 목록의 `data.resumes`에 표시되는지 확인합니다.
3. `http://localhost:5173`을 새로고침합니다.
4. 경험 카드와 이력서 상세를 열어 원문 및 근거가 맞는지 확인합니다.
5. JD와 자기소개서 문항을 입력해 추천 결과가 반환되는지 확인합니다.

목록 API에는 데이터가 있는데 프론트가 비어 있다면 요청의 `user_id`와 `.env`의 `VITE_USER_ID`가 같은지 먼저 확인합니다.

## 7. 서비스 종료와 재실행

데이터를 보존하며 종료:

```bash
docker compose down
```

기존 데이터를 유지한 채 다시 실행:

```bash
docker compose up -d
```

코드 또는 환경 변수를 변경한 뒤 다시 빌드:

```bash
docker compose up --build -d
```

로그 확인:

```bash
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f postgres
```

## 8. 데이터 보존 및 초기화 주의

PostgreSQL 데이터는 저장소의 `infra/postgres/data`에 보존됩니다. 일반적인 `docker compose down`으로는 삭제되지 않습니다.

DB를 완전히 초기화해야 하는 경우에만 다음 절차를 사용합니다. 이 작업은 기존 데이터를 삭제하므로 데이터 담당자와 확인한 뒤 수행해야 합니다.

```bash
docker compose down
# infra/postgres/data의 기존 DB 파일을 별도로 백업한 뒤 초기화
docker compose up --build -d
```

동일 문서를 반복 등록하거나 같은 텍스트 문서에 처리 API를 반복 호출하면 경험이 중복될 수 있습니다. 데이터 담당자는 원본 파일명, `document_id`, 처리 시각을 별도로 기록하는 것이 안전합니다.

## 9. 문제 해결

### Docker daemon에 연결할 수 없음

```text
Cannot connect to the Docker daemon
```

Docker Desktop을 실행하고 엔진 준비가 끝난 뒤 다시 시도합니다.

### 프론트는 열리지만 목록이 비어 있음

- 실제로 문서 처리 API까지 호출했는지 확인합니다.
- `VITE_USER_ID`와 등록 요청의 `user_id`가 같은지 확인합니다.
- `docker compose logs backend`에서 처리 실패 여부를 확인합니다.
- OpenAI 모드라면 API 키, 잔액, 모델 접근 권한을 확인합니다.

### PDF에서 경험이 생성되지 않음

- PDF가 암호화됐거나 이미지 스캔본인지 확인합니다.
- PDF에서 텍스트를 선택·복사할 수 있는지 확인합니다.
- `process_document=true`로 요청했는지 확인합니다.

### OpenAI 설정을 변경했는데 fake 결과가 나옴

`.env` 저장 후 컨테이너를 다시 생성하고 실제 적용값을 확인합니다.

```bash
docker compose up --build -d backend frontend
docker compose exec backend env | grep -E 'LLM_PROVIDER|EMBEDDING_PROVIDER|LLM_MODEL'
```

API 키 자체는 로그나 화면에 출력하지 않습니다.
