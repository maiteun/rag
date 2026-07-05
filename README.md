# KHU:DArchive

> KHUDA 9기 · 정기학술제

## 소개

KHU:DArchive는 사용자의 자기소개서, 이력서, 포트폴리오 메모 등 흩어진 커리어 기록을 경험 단위로 정리하고, JD/문항별로 적합한 경험을 추천한 뒤 자기소개서 초안까지 작성해주는 경험 기반 자기소개서 작성 보조 프로젝트입니다.

## 팀원

| 이름 | 역할 | 주요 내용 |
| :---: | :--- | :--- |
| 김연길 | 경험 전처리 | 사용자 경험 입력 처리, Notion MCP 기반 경험 추출, 서버 모델 형식에 맞춘 데이터 패키징 |
| 김정원 | 프론트엔드 | 사용자 화면 및 주요 UI/UX 구현 |
| 서지은 | RAG 파이프라인 | 사용자 질의 기반 경험 추천, 프롬프트 증강, LLM 기반 자기소개서 초안 생성 |
| 신진수 | CRUD API | 일반 도메인 CRUD API 구현 및 백엔드 기능 연동 |

## 대표 사진

![대표 사진 1](docs/assets/image1.png)

![대표 사진 2](docs/assets/image2.png)

## 기술 스택

- `Backend: Python, FastAPI, SQLAlchemy, Alembic, Pydantic`
- `Database: PostgreSQL, pgvector`
- `AI: LangChain, OpenAI LLM, OpenAI Embeddings`
- `Infrastructure: Docker Compose`  
- `Test: pytest`

## MVP 범위

1. 과거 기록 입력 및 원문 보존
2. 경험 단위 구조화와 출처 추적
3. 경험 Vault 검색 및 JD/문항 기반 경험 추천
4. 부족한 정보 보완 질문 생성 및 답변 반영
5. 추천 경험과 원문 근거를 활용한 자기소개서 초안 생성

## 구조

```text
.
├── apps/
│   ├── backend/          # FastAPI backend
│   └── frontend/         # frontend workspace
├── packages/
│   └── api-client/       # generated API client workspace
├── infra/
│   └── postgres/         # local PostgreSQL/pgvector setup
├── docs/                 # project documentation
├── scripts/              # utility scripts
├── docker-compose.yml
└── README.md
```

## 빠른 실행

Docker Desktop을 실행한 뒤 저장소 루트에서 전체 서비스를 시작합니다.

```bash
docker compose up --build
```

최초 실행이라면 별도 터미널에서 데모 데이터를 생성합니다.

```bash
python3 scripts/seed_demo.py
```

- 프론트엔드: `http://localhost:5173`
- API 문서: `http://localhost:8000/docs`
- 상태 확인: `http://localhost:8000/health`

프론트엔드는 Compose 빌드 시 API 모드로 설정되고 `/api` 요청을 백엔드 컨테이너로 전달합니다. 상세한 로컬 개발 절차와 OpenAI provider 설정은 [로컬 개발 및 실행](docs/development.md)을 참고합니다.

## 문서

- [전체 실행 및 데이터 투입 가이드](docs/howtorun.md)
- [프로젝트 개요](docs/project.md)
- [사용자 시나리오](docs/scenarios.md)
- [시스템 구성](docs/architecture.md)
- [API 문서](docs/api.md)
- [로컬 개발 및 실행](docs/development.md)
- [데이터 투입 인수인계](docs/data-import.md)
