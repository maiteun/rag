# KHU:DArchive

> KHUDA 9기 · 정기학술제

## 소개

KHU:DArchive는 사용자의 자기소개서, 이력서, 포트폴리오 메모 등 흩어진 커리어 기록을 경험 단위로 정리하고, JD/문항별로 적합한 경험을 추천하는 경험 저장소 프로젝트입니다.

## 팀원

| 이름 | 역할 |
| :---: | :--- |
| 김연길 | [역할] |
| 김정원 | [역할] |
| 서지은 | [역할] |
| 신진수 | [역할] |

## 대표 사진

![대표 사진 1](docs/assets/image1.png)

![대표 사진 2](docs/assets/image2.png)

## 기술 스택

- `Backend: Python, FastAPI, SQLAlchemy, Alembic, Pydantic`
- `Database: PostgreSQL, pgvector`
- `AI: LangChain, OpenAI LLM, OpenAI Embeddings`
- `Infrastructure: Docker Compose`
- `Test: pytest`

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

## 문서

- [프로젝트 개요](docs/project.md)
- [사용자 시나리오](docs/scenarios.md)
- [시스템 구성](docs/architecture.md)
- [API 문서](docs/api.md)
- [로컬 개발 및 실행](docs/development.md)
