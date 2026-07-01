# API 문서

API 계약은 FastAPI route와 Pydantic schema를 기준으로 관리합니다.

OpenAPI 산출물:

- [openapi.json](openapi/openapi.json)
- [openapi.yaml](openapi/openapi.yaml)

## 현재 구현된 주요 API

| Method | Path | 설명 |
| --- | --- | --- |
| GET | `/health` | 서버 상태 확인 |
| POST | `/api/documents/text` | 텍스트 기록 입력 |
| POST | `/api/documents/{document_id}/process` | 입력 문서 처리 |
| GET | `/api/documents/{document_id}/processing-result` | 문서 처리 결과 조회 |
| GET | `/api/experiences?user_id={user_id}` | 사용자 경험 목록 조회 |
| GET | `/api/experiences/{experience_id}` | 경험 상세 조회 |
| POST | `/api/experience-questions/{question_id}/answer` | 보완 질문 답변 |
| POST | `/api/retrieval/search` | 경험 검색 |

## MVP 예정 API

MVP 범위가 자기소개서 초안 생성까지 확장되면서 다음 API가 추가되어야 합니다.

| Method | Path | 설명 |
| --- | --- | --- |
| POST | `/api/recommendations/experiences` | JD/문항 기반 경험 추천 |
| POST | `/api/cover-letters/drafts` | 추천 경험 기반 자기소개서 초안 생성 |

## API 사용 순서

```text
문서 입력
  -> 문서 처리
  -> 처리 결과 조회
  -> 경험 상세 조회
  -> JD/문항 입력
  -> 경험 추천 요청
  -> 추천 결과 확인
  -> 보완 질문 답변
  -> 자기소개서 초안 생성 요청
  -> 초안 본문과 사용 근거 확인
```

## 텍스트 입력 예시

```json
{
  "user_id": "00000000-0000-0000-0000-000000000001",
  "source_type": "cover_letter",
  "title": "백엔드 프로젝트 경험 자기소개서",
  "text": "저는 FastAPI와 PostgreSQL을 사용해 사용자 맞춤 추천 API를 개발했습니다. 기존 추천 결과 응답 시간이 평균 1.8초로 느려 사용성이 떨어지는 문제가 있었습니다. 저는 백엔드 개발자로서 API 구조를 재설계하고, 쿼리 병목을 분석해 인덱스를 추가했으며, 자주 조회되는 데이터를 캐싱했습니다. 그 결과 평균 응답 시간이 1.8초에서 0.9초로 감소했고, 테스트 사용자 만족도도 개선되었습니다. 이 경험을 통해 성능 개선은 코드 최적화뿐 아니라 데이터 접근 패턴을 함께 봐야 한다는 점을 배웠습니다."
}
```

## 자기소개서 초안 생성 요청 예시

```json
{
  "user_id": "00000000-0000-0000-0000-000000000001",
  "target_role": "백엔드 개발자",
  "job_description": "FastAPI 기반 서비스 개발, PostgreSQL 성능 최적화, 사용자 맞춤 추천 기능 개발 경험 우대",
  "question": "본인의 프로젝트 경험 중 문제를 정의하고 해결한 사례를 설명해주세요.",
  "recommended_experience_ids": ["experience-id-1"],
  "length_limit": 700,
  "tone": "구체적이고 담백한 톤"
}
```

## 자기소개서 초안 생성 응답 예시

```json
{
  "draft": "FastAPI와 PostgreSQL을 활용한 사용자 맞춤 추천 API 개발 과정에서 응답 속도 저하 문제를 해결한 경험이 있습니다...",
  "used_experience_ids": ["experience-id-1"],
  "evidence": [
    {
      "experience_id": "experience-id-1",
      "source_excerpt": "기존 추천 결과 응답 시간이 평균 1.8초로 느려 사용성이 떨어지는 문제가 있었습니다."
    }
  ],
  "missing_information": [
    "해당 개선이 실제 사용자 행동 지표에 어떤 영향을 줬는지 추가하면 초안의 설득력이 높아집니다."
  ]
}
```
