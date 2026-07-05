# 로컬 개발 및 실행

## 요구 사항

- Python 3.11+
- Docker
- Docker Compose

## 환경 변수

로컬 백엔드를 직접 실행할 때는 루트의 `.env.example`을 참고해 `.env`를 설정합니다.

개발 흐름만 확인하려면 OpenAI API 키 없이 fake provider를 사용합니다. 이 설정은 실제 LLM 추론이나 의미 기반 embedding을 만들지 않고, 서버/API/DB 연결 흐름을 확인하기 위한 용도입니다.

```env
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/experience_vault
LLM_PROVIDER=fake
LLM_MODEL=gpt-5.4-mini
EMBEDDING_PROVIDER=fake
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536
OPENAI_API_KEY=
```

실제 문서에서 경험을 추출하고 RAG 검색에 사용할 embedding을 생성하려면 OpenAI provider와 API 키를 설정합니다.

```env
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/experience_vault
LLM_PROVIDER=openai
LLM_MODEL=gpt-5.4-mini
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536
OPENAI_API_KEY=sk-...
```

`LLM_MODEL`은 비용과 속도를 고려한 기본 추천값으로 `gpt-5.4-mini`를 사용합니다. 품질이 더 중요하면 `gpt-5.5`, 대량 테스트처럼 비용이 더 중요하면 `gpt-5.4-nano`를 사용할 수 있습니다. Embedding은 `text-embedding-3-small`과 `1536` 차원을 유지합니다.

Compose는 루트 `.env`의 `LLM_PROVIDER`, `LLM_MODEL`, `EMBEDDING_PROVIDER`, `EMBEDDING_MODEL`, `EMBEDDING_DIMENSION`, `OPENAI_API_KEY`, `NOTION_API_TOKEN`, `VITE_USER_ID`를 읽습니다. 값을 바꾼 뒤에는 백엔드 설정과 프론트 빌드에 반영되도록 `docker compose up --build`를 다시 실행합니다. Compose 내부 DB 주소를 직접 바꿔야 할 때만 `DATABASE_URL` 대신 `BACKEND_DATABASE_URL`을 사용합니다.

## 개발 모드: DB만 Docker Compose로 실행

백엔드 코드를 자주 수정하는 개발 중에는 PostgreSQL만 Docker Compose로 띄우고, FastAPI 서버는 로컬에서 실행하는 방식을 권장합니다.

```bash
docker compose up -d postgres
```

백엔드 의존성을 설치합니다.

```bash
cd apps/backend
python -m pip install -e ".[test]"
```

DB 마이그레이션을 실행합니다.

```bash
alembic upgrade head
```

FastAPI 서버를 실행합니다.

```bash
uvicorn app.main:app --reload
```

서버 실행 후 아래 주소에서 API를 확인할 수 있습니다.

- `http://localhost:8000/docs`
- `http://localhost:8000/redoc`
- `http://localhost:8000/openapi.json`

## 전체 실행: DB, 백엔드, 프론트엔드 함께 실행

팀 공유, 데모, 통합 실행 확인이 필요할 때는 Compose로 PostgreSQL, 백엔드, 프론트엔드를 함께 실행합니다.

```bash
docker compose up --build
```

백엔드 컨테이너는 `postgres` 서비스가 준비된 뒤 마이그레이션과 FastAPI 서버를 시작합니다. 프론트엔드는 백엔드 health check가 통과하면 시작하며, `/api` 요청을 내부 백엔드 서비스로 전달합니다.

전체 실행 주소:

- 프론트엔드: `http://localhost:5173`
- `http://localhost:8000/docs`
- `http://localhost:8000/redoc`
- `http://localhost:8000/openapi.json`

최초 실행 시 DB는 비어 있습니다. fake provider로 화면에 표시할 데모 이력서와 경험을 생성합니다.

```bash
python3 scripts/seed_demo.py
```

스크립트는 동일 사용자의 경험이 이미 있으면 중복 생성을 건너뜁니다. 강제로 추가하려면 `--force`를 사용합니다.

## 서비스별 실행

Compose에 백엔드 서비스가 포함되어 있어도 특정 서비스만 실행할 수 있습니다.

DB만 실행:

```bash
docker compose up -d postgres
```

백엔드까지 함께 실행:

```bash
docker compose up --build postgres backend
```

프론트엔드까지 전체 실행:

```bash
docker compose up --build
```

## 프론트엔드 로컬 개발

백엔드를 Compose로 실행하고 프론트엔드만 Vite 개발 서버로 실행하려면 `apps/frontend/.env.local`을 생성합니다.

```env
VITE_DATA_MODE=api
VITE_API_BASE_URL=http://localhost:8000/api
VITE_USER_ID=00000000-0000-0000-0000-000000000001
```

```bash
cd apps/frontend
npm install
npm run dev
```

실행 중인 서비스를 종료합니다.

```bash
docker compose down
```

DB 볼륨까지 초기화해야 할 때만 아래 명령을 사용합니다.

```bash
docker compose down -v
```

## 테스트

단위 테스트와 서비스 테스트는 백엔드 디렉터리에서 실행합니다.

```bash
cd apps/backend
python -m pytest -q
```

## OpenAPI Export

OpenAPI 산출물을 갱신합니다.

```bash
python scripts/export_openapi.py
```

생성 파일:

- `docs/openapi/openapi.json`
- `docs/openapi/openapi.yaml`

MVP 범위에는 경험 추천 API와 자기소개서 초안 생성 API가 포함되므로, 해당 route를 구현한 뒤 OpenAPI 산출물을 다시 export해야 합니다.
