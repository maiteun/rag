# 로컬 개발 및 실행

## 요구 사항

- Python 3.11+
- Docker
- Docker Compose

## 환경 변수

로컬 백엔드를 직접 실행할 때는 루트의 `.env.example`을 참고해 `.env`를 설정합니다.

```env
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/experience_vault
LLM_PROVIDER=fake
LLM_MODEL=gpt-4.1-mini
EMBEDDING_PROVIDER=fake
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536
OPENAI_API_KEY=
```

기본값은 fake LLM과 fake embedding을 사용하므로 OpenAI API 키 없이 로컬 테스트가 가능합니다.

OpenAI 연동을 사용할 때만 아래 값을 설정합니다.

```env
LLM_PROVIDER=openai
EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=...
```

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

## 전체 실행: DB와 백엔드를 함께 실행

팀 공유, 데모, 통합 실행 확인이 필요할 때는 Compose로 PostgreSQL과 백엔드를 함께 실행합니다.

```bash
docker compose up --build
```

백엔드 컨테이너는 `postgres` 서비스가 준비된 뒤 `alembic upgrade head`를 실행하고, 이후 FastAPI 서버를 `0.0.0.0:8000`으로 시작합니다.

전체 실행에서도 API 주소는 동일합니다.

- `http://localhost:8000/docs`
- `http://localhost:8000/redoc`
- `http://localhost:8000/openapi.json`

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
