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
| POST | `/api/documents/pdf` | PDF 기록 업로드 및 처리 |
| POST | `/api/documents/{document_id}/process` | 입력 문서 처리 |
| GET | `/api/documents/{document_id}/processing-result` | 문서 처리 결과 조회 |
| GET | `/api/experiences?user_id={user_id}` | 사용자 경험 목록 조회 |
| GET | `/api/experiences/{experience_id}` | 경험 상세 조회 |
| POST | `/api/experience-questions/{question_id}/answer` | 보완 질문 답변 |
| POST | `/api/retrieval/search` | 경험 검색 |
| POST | `/api/notion/workspaces/import` | Notion 워크스페이스 페이지 가져오기 |
| POST | `/api/matches` | JD/문항 매칭 요청 생성 |
| GET | `/api/matches/{match_id}` | 매칭 결과 조회 (폴링용) |
| GET | `/api/resumes?user_id={user_id}` | 과거 이력서 목록 조회 |
| GET | `/api/resumes/{resume_id}` | 과거 이력서 상세 조회 |

## 공통 응답 구조

`/health`를 제외한 모든 API는 공통 형식으로 응답합니다. 값이 없는 필드는 응답에서 제외됩니다.

성공 응답 (조회는 200, 생성은 201):

```json
{
  "success": true,
  "status": 201,
  "message": "리소스가 생성되었습니다.",
  "data": {
    "document_id": "...",
    "status": "processed"
  }
}
```

실패 응답 (에러 코드는 `도메인_상태코드_카운팅` 형식):

```json
{
  "success": false,
  "status": 404,
  "message": "존재하지 않는 문서입니다.",
  "code": "DOC_404_001",
  "meta": {
    "path": "/api/documents/xxx/processing-result",
    "timestamp": 1783000000000
  }
}
```

요청 본문 검증 실패는 400과 `COM_400_002`로 응답합니다. 에러 코드 전체 목록은 `apps/backend/app/core/codes.py`를 참고하세요.

## MVP 예정 API

MVP 범위가 자기소개서 초안 생성까지 확장되면서 다음 API가 추가되어야 합니다.

| Method | Path | 설명 |
| --- | --- | --- |
| POST | `/api/cover-letters/drafts` | 사용자가 선택한 경험 기반 자기소개서 초안 생성 |

경험 추천은 별도 API 대신 매칭 API(`POST /api/matches`) 내부의 추천 엔진으로 동작합니다. 현재 구현은 `RecommendationEngine`을 통해 경험 chunk를 검색하고, experience 단위로 후보를 묶은 뒤 추천 신호와 근거를 반환합니다.

## 매칭 API 사용 방법

`POST /api/matches`로 요청을 만들고, `GET /api/matches/{match_id}`를 폴링해 결과를 가져옵니다. status가 `completed`가 되면 문항별 recommendations가 채워집니다.

요청:

```json
{
  "user_id": "00000000-0000-0000-0000-000000000001",
  "job_description": "FastAPI 기반 서비스 개발 ...",
  "questions": ["문제 해결 경험을 서술하시오.", "협업 경험을 서술하시오."]
}
```

조회 응답의 data:

```json
{
  "id": "match_123",
  "status": "completed",
  "job_description": "...",
  "questions": [
    {
      "id": "q1",
      "text": "문제 해결 경험을 서술하시오.",
      "recommendations": [
        { "experience_id": "exp_1", "rank": 1, "score": 0.87, "reason": "문제와 해결 과정이 명확함" }
      ]
    }
  ],
  "created_at": "2026-07-03T12:00:00Z"
}
```

## API 사용 순서

```text
문서 입력
  -> 문서 처리
  -> 처리 결과 조회
  -> 경험 상세 조회
  -> JD/문항 입력
  -> 경험 추천 요청
  -> 추천 결과 확인
  -> 문항별 사용할 경험 선택
  -> 보완 질문 답변
  -> 자기소개서 초안 생성 요청
  -> 초안 본문과 사용 근거 확인
  -> 사이트 내 수정 및 문항별 txt/md export
```

## 경험 추천 응답 개념

추천 API는 문항별 top-k 경험 후보를 반환해야 합니다. 각 후보에는 최소한 경험 ID, 추천/보류/비추천 판단, 추천 이유, 추천하지 않는 이유 또는 주의점, 원문 근거, 부족한 정보가 포함되어야 합니다.

사용자는 이 결과를 검토한 뒤 초안 생성에 사용할 경험을 직접 선택합니다. 보완 질문은 사용자가 선택한 경험을 기준으로 생성되며, 초안 생성 요청은 추천 결과 전체가 아니라 사용자가 선택한 경험 ID 목록을 명시적으로 받아야 합니다.

## 경험 상세 응답의 facet

`GET /api/experiences/{experience_id}` 응답에는 `facets` 배열이 포함됩니다. 각 facet은 다음 구조를 가집니다.

```json
{
  "capability": "문제 정의 재구성",
  "theme": "프로젝트 수행",
  "label": "전국 평균 비교 대신 지형별 분석 구조로 문제를 다시 정의했다",
  "situation": "원문에 근거가 있는 상황 또는 문제",
  "action": "본인이 수행한 구체적 행동, 판단, 방법",
  "result": "결과, 성과, 배움",
  "details": ["세부 근거 문장"],
  "evidence": ["원문 인용"]
}
```

`theme`은 검색 라우팅이 아니라 화면 그룹핑용입니다. 허용값은 `프로젝트 수행`, `데이터 분석`, `기술 구현`, `협업`, `커뮤니케이션`, `문제 해결`, `성과`, `학습`입니다.

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
  "selected_experience_ids": ["experience-id-1"],
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
  ],
  "exports": {
    "txt": "FastAPI와 PostgreSQL을 활용한 사용자 맞춤 추천 API 개발 과정에서...",
    "markdown": "FastAPI와 PostgreSQL을 활용한 사용자 맞춤 추천 API 개발 과정에서..."
  }
}
```
