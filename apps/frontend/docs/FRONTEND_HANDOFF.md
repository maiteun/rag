# 프론트엔드 구현 핸드오프

## 1. 프로젝트 정의

과거 이력서와 경험 기록을 한곳에서 조회하고, JD와 자기소개서 문항을 입력하면 문항별로 적합한 경험을 추천하는 서비스다.

이 서비스는 자기소개서 완성 문장을 생성하지 않는다. 핵심 기능은 다음 두 가지다.

1. 저장된 전체 경험과 과거 이력서를 조회한다.
2. JD와 문항을 기준으로 관련 경험의 순위, 추천 이유, 근거를 보여준다.

핵심 사용자 질문은 다음과 같다.

> 이 문항에 내 경험 중 무엇을 써야 하는가?

## 2. MVP 범위

### 포함

- 전체 경험 목록 조회
- 경험 상세 조회
- 과거 이력서 목록 조회
- 과거 이력서 상세/PDF 조회
- JD 및 복수 문항 입력
- 비동기 매칭 요청 생성
- 매칭 상태 polling
- 문항별 추천 경험 순위 표시
- 추천 이유 및 매칭 수준 표시
- 추천 경험에서 경험 상세로 이동
- 추천 경험과 그 외 경험 비교

### 제외

- 사용자 로그인 및 다중 사용자 관리
- 경험 생성, 수정, 삭제
- 이력서 업로드 및 파싱 UI
- 추천 경험 선택 결과 저장
- 자기소개서 완성 문장 생성
- 문체 학습 및 첨삭
- Notion/GitHub 실시간 연동
- MCP
- ATS 점수화

추천 경험을 클릭하거나 화면에서 임시 선택하는 것은 프론트엔드 로컬 상태로 처리한다. 서버에는 저장하지 않는다.

## 3. 권장 기술 스택

현재 프로젝트의 프론트엔드 스택을 그대로 사용할 수 있다.

- React 19
- TypeScript
- Vite
- Tailwind CSS 4

새 워크스페이스에서도 같은 구성을 권장한다. API 상태 관리 라이브러리가 필요하면 TanStack Query를 추가할 수 있지만, MVP 규모에서는 `fetch`와 작은 API 모듈로도 충분하다.

## 4. 정보 구조 및 라우트

```text
/
└─ 매칭 작업대
   ├─ 경험 블록
   ├─ 과거 이력서 블록
   ├─ JD·문항 캔버스
   └─ 상세 modal overlay
```

MVP는 하나의 작업대 화면을 중심으로 구현한다. 경험이나 이력서를 클릭해도 현재 작업대가 사라지면 안 된다. 상세 정보는 modal overlay로 표시한다.

상세 modal 상태를 URL에 반영하는 것은 선택 사항이다. 예를 들어 `/experiences/:experienceId`를 background route로 사용할 수 있지만, 사용자에게는 페이지 전환이 아니라 현재 화면 위 modal로 보여야 한다.

### 전역 내비게이션

- 경험 관리
- 문항-경험 매칭
- 과거 이력서

와이어프레임 기준으로 `/`는 별도 초기 선택 화면이다. 중앙에 `경험 관리`, `문항-경험 매칭` 두 개의 진입 카드를 배치한다.

## 5. 사용자 플로우

### 5.1 경험 조회

```text
경험 목록
→ 경험 카드 클릭
→ 현재 화면 위 경험 상세 modal
→ 역할, 문제, 행동, 성과, 기술, 근거 자료 확인
→ modal 닫기 후 기존 목록 위치와 매칭 상태 유지
```

### 5.2 이력서 조회

```text
과거 이력서 목록
→ 이력서 클릭
→ 현재 화면 위 이력서 상세 modal
→ PDF 또는 추출 텍스트 확인
→ 해당 이력서에서 추출된 경험으로 이동
```

### 5.3 문항-경험 매칭

```text
초기 화면에서 문항-경험 매칭 선택
→ 매칭 입력 모달 열기
→ JD 탭과 문항 탭에 내용 입력
→ match request 생성
→ 분석 중 모달
→ GET /api/matches/{matchId} polling
→ 경험·이력서/JD·문항/최근 이력서 블록으로 구성된 작업대
→ 추천 경험 클릭
→ 현재 화면 위 경험 상세 modal
```

## 6. 화면 명세

### 6.1 초기 선택 화면

목적: 사용자가 `경험 관리`와 `문항-경험 매칭` 중 작업을 선택한다.

와이어프레임 구조:

```text
┌──────────────────────────────────────────┐
│ project name                             │
│                                          │
│          ┌──────────┐ ┌──────────┐       │
│          │ 경험 관리 │ │문항-경험 │       │
│          │          │ │  매칭    │       │
│          └──────────┘ └──────────┘       │
│                                          │
└──────────────────────────────────────────┘
```

- 좌측 상단에 서비스명 또는 로고를 배치한다.
- 중앙에 동일한 크기의 두 진입 카드를 배치한다.
- `경험 관리` 클릭 시 같은 작업대 화면을 열고 경험 블록에 focus한다. 경험 목록 전용 페이지로 전환하지 않는다.
- `문항-경험 매칭` 클릭 시 현재 화면 위에 입력 모달을 연다.
- 카드는 버튼 역할을 하므로 hover, focus, active 상태가 필요하다.

### 6.2 경험 목록 블록

목적: 저장된 경험 전체를 빠르게 탐색한다.

필수 요소:

- 블록 제목
- 경험 개수
- 검색 입력
- 기술/역량 필터는 선택 사항
- 경험 카드 또는 행 목록
- 경험 제목, 기간, 요약, 기술 태그
- 빈 상태와 오류 상태
- 블록 내부 무한 스크롤

경험 목록은 별도 페이지가 아니라 작업대 좌측 블록에 표시한다. 브라우저 전체 페이지가 아니라 목록 컨테이너 내부만 스크롤되어야 한다.

매칭 결과가 있을 때의 정렬 구조:

```text
추천 경험 1
추천 경험 2
추천 경험 3
-------------------- 점선 구분선
그 외 경험 1
그 외 경험 2
...
```

- 현재 문항에서 RAG가 추천한 경험을 `rank` 순으로 먼저 표시한다.
- 점선 구분선 아래에 추천되지 않은 나머지 경험을 표시한다.
- 추천 경험 ID는 `GET /api/matches/{matchId}` 응답에서 가져온다.
- 추천/비추천 그룹 구분은 프론트엔드가 `experience_id`로 계산한다.
- 매칭 전에는 전체 경험만 표시하며 구분선을 렌더링하지 않는다.
- 목록 끝에 가까워지면 다음 페이지를 불러온다. 실제 pagination 방식은 `apps/backend` 구현을 따른다.

### 6.3 경험 상세

필수 요소:

- 제목과 기간
- 한 줄 요약
- 역할
- 문제 상황
- 수행 행동
- 결과/성과
- 기술 및 역량 태그
- 근거 자료 목록
- 연결된 과거 이력서 링크

경험 카드를 클릭하면 현재 화면 위에 modal을 띄운다. 별도 화면으로 전환하거나 작업대 상태를 초기화하지 않는다. modal을 닫으면 기존 스크롤 위치, 선택 문항, match 결과가 그대로 유지되어야 한다.

### 6.4 과거 이력서 목록 블록

필수 요소:

- 제목
- 파일명
- 생성/등록일
- 추출된 경험 개수
- 이력서 상세 modal 열기
- 블록 내부 무한 스크롤

과거 이력서 목록도 별도 페이지가 아니라 좌측 하단의 접이식 블록이다.

- 기본 상태에서는 header만 보이거나 최소 높이로 접혀 있을 수 있다.
- 펼치면 좌측 영역에서 경험 목록과 이력서 목록이 각각 약 절반 높이를 차지한다.
- 펼침/접힘 애니메이션 중에도 전체 작업대 높이는 변하지 않는다.
- 이력서 블록이 커지는 만큼 경험 목록 블록의 높이가 줄어든다.
- 경험과 이력서 목록은 각자의 컨테이너 안에서 독립적으로 스크롤한다.

### 6.5 과거 이력서 상세

필수 요소:

- 이력서 메타데이터
- PDF viewer 또는 파일 열기
- 추출 텍스트
- 이력서에서 추출된 경험 목록

이력서 클릭 시 현재 작업대 위에 modal을 띄운다. PDF viewer 구현이 부담되면 modal 내부에서 브라우저 기본 PDF embed를 사용한다. 새 탭 열기는 보조 액션으로만 제공하고 기본 동작으로 사용하지 않는다.

### 6.6 매칭 요청 입력 모달

와이어프레임에서는 별도 페이지가 아니라 초기 화면 위에 모달로 표시한다.

```text
┌──────────────────────────────────┐
│ 문항-경험 매칭                × │
│ [ JD ] [ 문항 ]                  │
│ ┌──────────────────────────────┐ │
│ │ 입력 영역                    │ │
│ │                              │ │
│ └──────────────────────────────┘ │
│                       [매칭하기] │
└──────────────────────────────────┘
```

필수 요소:

- 회사명: 선택 입력
- 직무명: 선택 입력
- `JD`, `문항` segmented tab
- JD textarea
- 자기소개서 문항 입력 영역
- 문항 추가/삭제
- 분석 시작 버튼
- 모달 닫기 버튼
- 입력 검증 메시지

탭을 이동해도 입력값이 유지되어야 한다. `매칭하기` 버튼은 JD와 문항이 모두 유효할 때만 활성화한다.

검증 규칙:

- JD는 필수
- 문항은 최소 1개
- 빈 문항 제출 금지
- 중복 제출 방지를 위해 요청 중 버튼 비활성화

### 6.7 분석 중 모달

입력 모달과 동일한 위치와 크기를 유지한 채 분석 상태로 전환한다. 화면이 갑자기 이동하지 않도록 modal shell은 재사용한다.

필수 요소:

- 처리 중임을 알리는 상태
- 로딩 indicator 또는 짧은 로딩 문구
- 실패 시 오류 메시지와 다시 시도 버튼

MVP에서는 세부 진행률을 만들지 않는다. `queued`, `processing`, `completed`, `failed`만 처리한다.

### 6.8 매칭 결과

첨부된 최신 레퍼런스 기준으로 결과 화면은 단순한 3열 grid가 아니라, 각 기능이 독립적인 surface를 갖는 **블록형 작업대**다.

```text
┌─────────────────────────────────────────────────────────────┐
│ 작업대 제목 / 상태 / 요약 액션                               │
├──────────────┬──────────────────────────────┬───────────────┤
│ ┌ 경험 블록 ┐ │ ┌ JD·문항 캔버스          ┐ │ ┌ 최근 이력서 ┐ │
│ │ 추천 경험 │ │ │ JD 링크 또는 직접 입력   │ │ │ 이력서 카드  │ │
│ │ ----------│ │ │ 문항 탭 및 분석 결과      │ │ │ 이력서 카드  │ │
│ │ 그 외 경험│ │ │                          │ │ │              │ │
│ │            │ │ │                          │ │ │              │ │
│ ├────────────┤ │ └──────────────────────────┘ │ └──────────────┘ │
│ │과거 이력서│ │                                              │
│ └────────────┘ │                                              │
└──────────────┴──────────────────────────────┴───────────────┘
```

필수 요소:

- 좌측 `경험 블록` surface
- 좌측 하단 `과거 이력서` expandable surface
- 중앙 `JD·문항 캔버스` surface
- 우측 `최근 이력서` surface
- 문항 번호 탭
- 선택 문항 원문
- 문항 의도와 요구 역량
- 순위가 표시된 추천 경험
- 추천 이유
- 매칭 수준
- 경험 상세 열기
- 과거 이력서 접기/펼치기

각 블록은 흰색 배경, 구분 가능한 border, 독립된 header와 scroll region을 가진다. page section 전체를 하나의 큰 카드처럼 처리하지 않는다.

좌측 경험 블록:

- 현재 문항의 추천 경험을 순위대로 상단에 표시한다.
- 추천 카드에는 순위, 제목, 짧은 추천 이유를 표시한다.
- 추천 경험 다음에 점선 구분선을 표시한다.
- 추천되지 않은 경험은 구분선 아래에 표시한다.
- 경험 클릭 시 상세 modal을 연다.
- 경험 카드들은 좌측 경험 블록 안에서 무한 스크롤한다.
- 경험 카드의 위치가 겹쳐 보이는 장식은 레퍼런스의 시각 언어로만 참고하고, 실제 카드끼리 겹쳐 클릭 영역이 모호해지지 않게 한다.

좌측 과거 이력서 블록:

- 접힌 상태에서는 header만 보이거나 작은 높이를 사용한다.
- 펼친 상태에서는 좌측 가용 높이의 약 50%를 차지한다.
- 동시에 경험 블록도 약 50%로 줄어든다.
- 두 블록의 최소 높이를 설정해 header와 최소 한 개 항목이 보이게 한다.
- CSS grid row 또는 flex basis를 상태에 따라 변경한다.

중앙 JD·문항 캔버스:

- 상단에 문항 번호 탭을 표시한다.
- 탭 선택 시 해당 문항과 추천 결과를 교체한다.
- 매칭 전에는 JD 링크/직접 입력과 빈 상태를 표시한다.
- 매칭 후에는 문항별 추천 결과와 추천 이유를 표시한다.
- 자기소개서 작성 textarea로 오해되지 않도록 결과 영역임을 명확히 한다.

우측 최근 이력서 블록:

- 최근 또는 신호가 있는 이력서 카드를 표시한다.
- 이력서 클릭 시 상세 modal을 연다.
- 목록이 길면 블록 내부에서 무한 스크롤한다.
- 백엔드가 합격/면접 등의 신호를 제공하지 않으면 mock data에서만 badge를 보여주고 실제 API에서는 숨긴다.

`score`의 정의가 확정되지 않았다면 숫자 백분율 대신 `높음`, `보통`, `낮음`을 표시한다.

## 7. API 계약

이 문서의 API 예시는 프론트엔드 구현을 위한 예상 계약이다. 실제 작업 워크스페이스에서는 **저장소 root의 `apps/backend` 구현을 먼저 읽고**, 실제 route, schema, status code를 그 구현에 맞춘다.

백엔드가 아직 완성되지 않았거나 일부 endpoint가 없는 경우:

- 프론트엔드 작업을 중단하지 않는다.
- `apps/backend`에 존재하는 endpoint만 실제 API adapter로 연결한다.
- 없는 endpoint와 미완성 응답은 mock adapter로 대체한다.
- 화면 컴포넌트가 mock/real 여부를 알 필요 없게 동일한 TypeScript 타입으로 정규화한다.
- 프론트엔드 때문에 backend 코드를 임의로 수정하지 않는다.

Base URL과 데이터 모드는 환경변수로 관리한다.

```text
VITE_API_BASE_URL=http://localhost:8000/api
VITE_DATA_MODE=mock
```

예시 mode:

- `mock`: 모든 데이터를 fixture에서 제공
- `api`: `apps/backend`의 실제 API 사용
- `hybrid`: 구현된 endpoint는 실제 API, 나머지는 mock fallback

### 7.1 경험 목록

```http
GET /api/experiences
```

```json
{
  "experiences": [
    {
      "id": "exp_1",
      "title": "AI 자동화 프로젝트",
      "period": "2025.03 - 2025.06",
      "summary": "반복 업무를 자동화한 프로젝트",
      "skills": ["Python", "LLM API"]
    }
  ]
}
```

### 7.2 경험 상세

```http
GET /api/experiences/{experienceId}
```

```json
{
  "id": "exp_1",
  "title": "AI 자동화 프로젝트",
  "period": "2025.03 - 2025.06",
  "summary": "반복 업무를 자동화한 프로젝트",
  "role": "데이터 수집 및 자동화 파이프라인 구현",
  "problem": "반복적인 수작업으로 많은 시간이 소요됨",
  "actions": ["Python 기반 자동화 파이프라인 구현"],
  "outcomes": ["반복 작업 감소"],
  "skills": ["Python", "LLM API"],
  "evidence": [
    {
      "source_id": "resume_1",
      "source_type": "resume",
      "label": "2025 AI 직무 이력서",
      "page": 2
    }
  ]
}
```

### 7.3 이력서 목록

```http
GET /api/resumes
```

```json
{
  "resumes": [
    {
      "id": "resume_1",
      "title": "2025 AI 직무 이력서",
      "file_name": "resume_ai_2025.pdf",
      "created_at": "2025-11-03",
      "experience_count": 4
    }
  ]
}
```

### 7.4 이력서 상세 및 파일

```http
GET /api/resumes/{resumeId}
GET /api/resumes/{resumeId}/file
```

```json
{
  "id": "resume_1",
  "title": "2025 AI 직무 이력서",
  "file_name": "resume_ai_2025.pdf",
  "file_url": "/api/resumes/resume_1/file",
  "extracted_text": "...",
  "experience_ids": ["exp_1", "exp_3"]
}
```

### 7.5 매칭 요청 생성

```http
POST /api/matches
```

```json
{
  "company": "A사",
  "role": "백엔드 인턴",
  "job_description": "...",
  "questions": [
    "문제 해결 경험을 서술하시오.",
    "협업 경험을 서술하시오."
  ]
}
```

권장 응답 상태는 `202 Accepted`다.

```json
{
  "id": "match_123",
  "status": "queued"
}
```

### 7.6 매칭 상태 및 결과

```http
GET /api/matches/{matchId}
```

처리 중:

```json
{
  "id": "match_123",
  "status": "processing"
}
```

완료:

```json
{
  "id": "match_123",
  "status": "completed",
  "company": "A사",
  "role": "백엔드 인턴",
  "job_description": "...",
  "job_analysis": {
    "summary": "커머스 플랫폼 백엔드 개발",
    "required_skills": ["Spring", "SQL"],
    "competencies": ["문제 해결", "협업"]
  },
  "questions": [
    {
      "id": "q1",
      "text": "문제 해결 경험을 서술하시오.",
      "intent": "문제 해결 과정과 본인 기여 확인",
      "required_elements": ["문제 상황", "본인 역할", "해결 과정", "결과"],
      "recommendations": [
        {
          "experience_id": "exp_1",
          "rank": 1,
          "match_level": "high",
          "score": 0.87,
          "score_type": "hybrid_retrieval",
          "reason": "문제와 해결 과정이 명확하고 본인의 기술적 기여가 드러남"
        }
      ]
    }
  ]
}
```

실패:

```json
{
  "id": "match_123",
  "status": "failed",
  "error": {
    "code": "MATCH_PROCESSING_FAILED",
    "message": "경험 추천을 생성하지 못했습니다."
  }
}
```

## 8. Polling 동작

1. `POST /api/matches` 성공 후 `matchId`를 받는다.
2. `/matches/{matchId}`로 이동한다.
3. `GET /api/matches/{matchId}`를 호출한다.
4. `queued` 또는 `processing`이면 2초 후 다시 호출한다.
5. `completed`이면 polling을 중단하고 결과를 표시한다.
6. `failed`이면 polling을 중단하고 오류를 표시한다.
7. 컴포넌트 unmount 시 timer와 요청을 취소한다.

무한 polling을 막기 위해 프론트엔드 timeout을 둔다. MVP 권장값은 2분이다.

## 9. 추천 경험과 그 외 경험 구분

MVP에서는 프론트엔드가 구분한다.

```text
GET /api/matches/{matchId}
→ 선택 문항의 recommendation experience_id 목록

GET /api/experiences
→ 전체 경험 목록
```

추천 ID에 포함되면 추천 경험, 포함되지 않으면 그 외 경험으로 표시한다.

경험 데이터가 많아져 서버 pagination이 필요해질 때만 다음과 같은 결합 조회를 추가한다.

```http
GET /api/experiences?match_id={matchId}&question_id={questionId}
```

## 10. 프론트엔드 타입 초안

```ts
type MatchStatus = 'queued' | 'processing' | 'completed' | 'failed'
type MatchLevel = 'high' | 'medium' | 'low'

interface ExperienceSummary {
  id: string
  title: string
  period?: string
  summary: string
  skills: string[]
}

interface Recommendation {
  experience_id: string
  rank: number
  match_level: MatchLevel
  score?: number
  score_type?: string
  reason: string
}

interface MatchQuestion {
  id: string
  text: string
  intent?: string
  required_elements: string[]
  recommendations: Recommendation[]
}

interface MatchResult {
  id: string
  status: MatchStatus
  company?: string
  role?: string
  job_description?: string
  job_analysis?: {
    summary: string
    required_skills: string[]
    competencies: string[]
  }
  questions?: MatchQuestion[]
  error?: {
    code: string
    message: string
  }
}
```

## 11. 권장 컴포넌트 구조

```text
AppShell
├─ WorkspaceHeader
├─ MatchingWorkbench
│  ├─ ExperienceSourcesColumn
│  │  ├─ ExperienceBlock
│  │  │  ├─ RecommendedExperienceList
│  │  │  ├─ DottedGroupDivider
│  │  │  └─ OtherExperienceList
│  │  └─ ExpandableResumeBlock
│  ├─ JobQuestionCanvas
│  │  ├─ JobInputModeControl
│  │  ├─ QuestionNavigation
│  │  └─ RecommendationResult
│  └─ RecentResumeBlock
├─ ExperienceDetailModal
│  ├─ ExperienceHeader
│  ├─ ExperienceSections
│  └─ EvidenceList
├─ ResumeDetailModal
│  ├─ ResumeViewer
│  └─ LinkedExperienceList
├─ MatchCreateModal
│  ├─ JobDescriptionField
│  └─ QuestionFieldList
└─ MatchStatusModal
```

## 12. 상태별 UI 체크리스트

모든 데이터 화면은 다음 상태를 구현한다.

- loading
- empty
- success
- error

매칭 화면은 추가로 다음 상태가 필요하다.

- queued
- processing
- completed
- failed
- polling timeout

추천 결과가 0개인 경우 억지 추천 대신 다음 메시지를 표시한다.

> 현재 기록에서는 이 문항에 충분히 적합한 경험을 찾지 못했습니다.

## 13. Mock 우선 개발

백엔드 완성 전에는 API 응답 예시를 JSON fixture로 만들어 개발한다.

이 프로젝트에서는 화면이 먼저 완성되어야 하므로 기본 실행값을 `VITE_DATA_MODE=mock`으로 둔다. 새 워크스페이스의 `apps/backend`를 확인한 뒤 구현된 endpoint부터 `api` 또는 `hybrid` mode에 연결한다.

권장 fixture:

```text
src/mocks/
├─ experiences.json
├─ experience-detail.json
├─ resumes.json
├─ resume-detail.json
├─ match-processing.json
├─ match-completed.json
└─ match-failed.json
```

프론트엔드에서 mock과 실제 API를 쉽게 교체할 수 있도록 데이터 접근은 `src/api` 아래로 모은다.

```text
src/api/
├─ client.ts
├─ data-source.ts
├─ experiences.ts
├─ resumes.ts
└─ matches.ts
```

목록 mock에는 무한 스크롤을 확인할 수 있을 만큼 충분한 항목을 넣는다.

- 경험 최소 20개
- 이력서 최소 12개
- 추천 경험 3~5개
- 추천되지 않은 경험
- 다음 페이지 loading 상태
- 마지막 페이지 상태
- 빈 목록과 API 실패 상태

실제 backend가 pagination을 제공하지 않으면 mock adapter에서 page 단위로 잘라 반환하고, 실제 API 연결 시에는 전체 응답을 프론트엔드에서 점진적으로 노출해 내부 무한 스크롤 동작을 유지한다.

## 14. 시각 디자인 사양

### 색상

```css
:root {
  --color-page: #f4f4f4;
  --color-surface: #ffffff;
  --color-primary: #0033ff;
  --color-text: #171717;
  --color-text-muted: #737373;
  --color-border: #dedede;
  --color-divider: #cfcfcf;
}
```

- 전체 페이지 배경은 `#f4f4f4`다.
- 경험, 이력서, JD·문항 캔버스 등 주요 블록은 흰색 surface로 표시한다.
- primary color는 `#0033ff`이며 CSS variable로 관리해 나중에 한 곳에서 변경할 수 있게 한다.
- primary는 주요 CTA, active tab, focus ring, 선택/추천 강조에 제한적으로 사용한다.
- 화면을 여러 색으로 분할하지 않는다. 기본 팔레트는 흰색, 회색, 검정, primary blue다.
- 성공/실패 상태 색상이 필요하면 badge나 작은 상태 표시에만 사용한다.

### 블록

- 기능 단위마다 독립된 흰색 블록을 사용한다.
- 블록 안의 목록은 자체 header와 scroll region을 가진다.
- 블록끼리 겹치거나 블록 내부에 장식용 중첩 카드를 반복하지 않는다.
- 카드 radius는 8px 이하를 기본으로 하고, 기존 디자인 시스템이 있으면 그것을 따른다.
- shadow는 최소화하고 border와 배경 차이로 계층을 만든다.

### Modal

- 경험과 이력서 상세는 화면 중앙 modal로 표시한다.
- 배경에는 dimmed overlay를 적용하되 작업대 구조가 보일 정도로 유지한다.
- `Escape`, 닫기 버튼, overlay 클릭으로 닫을 수 있게 한다. 단, PDF 상호작용 중 accidental close를 방지한다.
- 열릴 때 focus를 modal 안으로 이동하고 닫힐 때 클릭했던 카드로 복귀시킨다.
- modal이 열려 있는 동안 배경 스크롤을 잠근다.

### 내부 스크롤과 높이

- desktop 작업대 높이는 `100dvh` 안에서 header를 제외한 나머지 영역을 사용한다.
- 브라우저 body가 길게 늘어나는 방식보다 각 블록 내부 scroll을 우선한다.
- 좌측 경험/이력서 블록은 `minmax(0, 1fr)`을 사용해 overflow가 상위 grid를 늘리지 않게 한다.
- 이력서 접힘: 경험 목록이 남은 높이 대부분을 차지한다.
- 이력서 펼침: 경험과 이력서가 약 `1fr 1fr`로 나뉜다.

## 15. Figma 반영 방법

현재 반영한 와이어프레임:

- `apps/frontend/docs/wireframe.png`
- 초기 선택 화면
- JD/문항 입력 모달
- 분석 중 모달
- 블록형 JD 매칭 작업대
- 경험 목록과 과거 이력서의 가변 높이 구조
- 경험, 이력서 상세 modal 요구사항

현재 와이어프레임은 데스크톱 핵심 플로우를 정의한다. 다음 상태는 이미지에 없으므로 구현 과정에서 이 문서의 요구사항을 기준으로 보완한다.

- 경험 관리 화면과 경험 상세
- 과거 이력서 상세/PDF 화면
- 입력 validation
- 분석 실패와 polling timeout
- 추천 경험 0개
- loading skeleton
- mobile/tablet 레이아웃
- hover/focus/disabled 상태

Figma 와이어프레임은 다음 중 하나로 전달하면 구현에 반영할 수 있다.

1. 접근 가능한 Figma 링크
2. 각 화면의 PNG/JPG 캡처
3. Figma에서 export한 PDF
4. 주요 frame을 이미지로 첨부

반영 가능한 항목:

- 화면별 레이아웃
- 내비게이션 구조
- 컴포넌트 분리
- spacing과 크기
- 색상과 typography
- 반응형 전환 방식
- modal, drawer, tab 등 상호작용
- loading, empty, error 상태

Figma 링크만 제공할 경우 접근 권한이 있어야 한다. 링크 접근이 어렵다면 desktop/mobile frame 캡처를 첨부하는 방식이 가장 확실하다.

Figma를 반영하기 전 확인할 사항:

- desktop과 mobile frame 존재 여부
- 클릭 후 이동 관계
- hover/focus/disabled 상태
- 긴 JD, 긴 문항, 긴 경험 제목 처리
- 추천 0개 및 처리 실패 상태
- PDF viewer가 와이어프레임에 포함되는지

## 16. 반응형 규칙

현재 와이어프레임은 wide desktop 기준이다.

### Desktop

- 작업대의 블록형 3-column 배치를 유지한다.
- 권장 폭 비율은 좌측 source column `20~24%`, 중앙 canvas `52~60%`, 우측 recent resume `20~24%`다.
- 좌측 column 내부에서 경험과 과거 이력서가 세로 공간을 공유한다.

### Tablet

- 경험 블록은 tab 또는 접이식 block으로 전환할 수 있다.
- 중앙 문항 패널을 기본 화면으로 둔다.
- 최근 이력서 블록은 tab으로 전환한다.

### Mobile

- 3열을 세로로 쌓지 않는다.
- `경험`, `문항`, `JD`를 상단 tab으로 전환한다.
- 입력 모달은 화면 전체를 사용하는 sheet/page로 전환한다.
- 문항 번호 탭은 가로 스크롤을 허용한다.
- 경험과 이력서 상세는 full-screen modal로 표시한다.

## 17. 구현 완료 기준

- 전체 경험 목록과 상세를 작업대 화면을 벗어나지 않고 탐색할 수 있다.
- 과거 이력서 목록과 파일을 modal에서 볼 수 있다.
- JD와 문항을 입력해 match request를 생성할 수 있다.
- 처리 상태에 따라 polling이 시작되고 종료된다.
- 완료 후 문항별 추천 경험이 순위대로 표시된다.
- 추천 이유와 매칭 수준을 확인할 수 있다.
- 추천 경험에서 경험 상세를 열 수 있다.
- 추천 경험과 그 외 경험을 구분해 볼 수 있다.
- 추천 경험 뒤에 점선 구분선과 그 외 경험이 표시된다.
- 경험/이력서 목록이 각 블록 내부에서 무한 스크롤한다.
- 과거 이력서 블록을 펼치면 경험 블록이 줄고 두 블록이 약 절반씩 높이를 사용한다.
- loading, empty, error, failed 상태가 구현되어 있다.
- mock API와 실제 API를 교체할 수 있는 구조다.
- 기본 실행에서 backend 없이 mock data로 전체 UI를 확인할 수 있다.
- 실제 API 계약은 작업 워크스페이스의 `apps/backend`를 기준으로 한다.
- page 배경 `#f4f4f4`, surface 흰색, primary `#0033ff`를 CSS variable로 사용한다.
- desktop과 mobile에서 텍스트 또는 컨트롤이 겹치지 않는다.
