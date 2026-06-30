# API Guide

FastAPI route와 Pydantic schema가 API 계약의 source of truth입니다.

OpenAPI 산출물:

- `docs/openapi/openapi.json`
- `docs/openapi/openapi.yaml`

## Health

- `GET /health`

## Documents

- `POST /api/documents/text`
- `POST /api/documents/{document_id}/process`
- `GET /api/documents/{document_id}/processing-result`

문서 입력 API는 사용자의 과거 기록 원문을 저장합니다.

문서 처리 API는 다음 흐름을 동기적으로 수행합니다.

1. 원문 조회
2. 텍스트 정제
3. LLM 기반 경험 추출
4. 경험 및 source evidence 저장
5. RAG chunk 생성
6. embedding 생성 및 저장
7. 보완 질문 생성

## Experiences

- `GET /api/experiences?user_id={user_id}`
- `GET /api/experiences/{experience_id}`

경험 목록과 상세 정보를 조회합니다.

상세 응답에는 출처와 보완 질문이 포함됩니다.

## Questions

- `POST /api/experience-questions/{question_id}/answer`

보완 질문 답변을 저장하고 경험 정보를 갱신합니다.

답변 반영 후 관련 chunk와 embedding도 다시 생성합니다.

## Retrieval

- `POST /api/retrieval/search`

사용자별 chunk를 대상으로 retrieval search를 수행합니다.

모든 검색은 `user_id` 기준으로 제한됩니다.

