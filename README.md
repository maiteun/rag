# [프로젝트 제목]

  > KHUDA 9기 · 정기학술제

  ## 소개
  KHUDA 9기 AIE 1조입니다!

  ## 팀원
  | 이름 | 역할 |
  | :---: | :--- |
  | 김연길 | [역할] |
  | 김정원 | [역할] |
  | 서지은 | [역할] |
  | 신진수 | [역할] |
  
  ## 대표 사진
  [대표 사진을 넣어주세요.]

## 프로젝트 요약

사용자의 과거 자기소개서, 이력서, 포트폴리오 메모를 경험 단위로 정리하고 RAG 검색에 사용할 수 있는 경험 vault를 만드는 백엔드 MVP입니다.

현재 범위는 추천 결과 생성이 아니라, 추천 단계가 사용할 데이터 파이프라인을 구축하는 것입니다.

## 빠른 시작

```bash
cd apps/backend
python -m pip install -e ".[test]"
python -m pytest -q
```

로컬 DB까지 실행하려면 다음 문서를 참고하세요.

- [개발 및 실행 가이드](docs/development.md)

## 문서

- [문서 홈](docs/README.md)
- [아키텍처](docs/architecture/README.md)
- [API 가이드](docs/api.md)
- [OpenAPI JSON](docs/openapi/openapi.json)
- [OpenAPI YAML](docs/openapi/openapi.yaml)

## 주요 경로

- `apps/backend`: FastAPI 백엔드 구현
- `apps/frontend`: 추후 프론트엔드 구현을 위한 placeholder
- `packages/api-client`: 추후 OpenAPI 기반 client 생성을 위한 placeholder
- `infra/postgres`: 로컬 PostgreSQL/pgvector 초기화
- `docs`: 세부 문서와 OpenAPI 산출물
- `scripts`: 보조 스크립트

## 현재 구현 범위

- 텍스트 기록 입력 및 원문 보존
- LLM 기반 경험 후보 추출
- 경험 출처, chunk, embedding 저장
- 부족한 정보에 대한 보완 질문 생성
- 질문 답변 반영 후 경험/chunk/embedding 갱신
- 사용자별 경험 조회 및 retrieval search API

## 제외 범위

- 프론트엔드 UI
- JD/문항 기반 경험 추천
- 자기소개서 초안 생성
- 면접 질문 생성
- ATS 점수화
- 배포 인프라
