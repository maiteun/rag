# 경험 입력 및 추출 파이프라인

이 문서는 KHU:DArchive가 사용자의 기록을 입력받아 구조화된 경험으로 저장하는 흐름을 정리합니다.

## 지원 입력 채널

현재 경험 입력 채널은 3개입니다. 세 채널 모두 최종적으로 `source_documents`에 원문을 저장한 뒤 같은 `DocumentProcessingService` 파이프라인을 탑니다.

| 채널 | API | 동작 |
| --- | --- | --- |
| 텍스트 | `POST /api/documents/text` 이후 `POST /api/documents/{document_id}/process` | 사용자가 직접 입력한 텍스트를 저장하고, 별도 처리 API로 경험을 추출합니다. |
| PDF | `POST /api/documents/pdf` | PDF 파일을 업로드하고, `pypdf`로 텍스트를 추출한 뒤 기본값으로 즉시 경험 추출까지 실행합니다. |
| Notion | `POST /api/notion/workspaces/import` | Notion root 페이지와 하위 페이지를 가져와 페이지별로 저장하고, 기본값으로 각 페이지를 경험 추출 처리합니다. |

## 공통 처리 흐름

```text
입력 채널
  -> source_documents 저장
  -> TextCleaningService
  -> ExperienceExtractionService
  -> 제목만 있는 빈 경험 draft 제거
  -> experiences 저장
  -> experience_sources 저장
  -> experience_chunks 생성
  -> EmbeddingService
  -> experience_questions 생성
```

공통 진입점은 `DocumentProcessingService`입니다. 텍스트, PDF, Notion 입력은 모두 이 서비스를 통해 경험 카드, 원문 evidence, 검색용 chunk, embedding, 보완 질문을 생성합니다.

## Notion 데모 흐름

현재 데모에서는 OAuth를 사용하지 않습니다. 사용자가 Notion internal integration token과 가져올 페이지 URL을 직접 입력하는 방식입니다.

사용자 흐름은 다음과 같습니다.

1. Notion Developers에서 internal integration을 생성합니다.
2. `secret_`으로 시작하는 integration token을 복사합니다.
3. 가져올 Notion 최상위 페이지를 엽니다.
4. 해당 페이지의 `Add connections`에서 1번에서 만든 integration을 연결합니다.
5. 프론트엔드에서 아래 값을 입력합니다.
   - Notion API token
   - Notion page URL
6. 백엔드는 URL에서 page ID를 파싱하고, root 페이지와 하위 페이지를 가져옵니다.

현재 백엔드는 `root_page_id`를 지원합니다. 프론트엔드에서 자연스럽게 쓰려면 다음 단계로 `root_page_url`도 지원하는 것이 좋습니다.

권장 요청 형태는 다음과 같습니다.

```json
{
  "user_id": "user-1",
  "notion_token": "secret_xxx",
  "root_page_url": "https://www.notion.so/.../Notion-3907736fa64880df9e2ee9302f483c27",
  "process_documents": true,
  "max_pages": 50
}
```

백엔드에서는 아래 우선순위로 처리하면 됩니다.

1. `root_page_id`가 있으면 그대로 사용합니다.
2. `root_page_id`가 없고 `root_page_url`이 있으면 URL에서 page ID를 파싱합니다.
3. 둘 다 없으면 integration이 접근 가능한 전체 페이지를 search API로 탐색합니다.

## Notion page ID 파싱

사용자가 page ID를 직접 입력하게 만들면 UX가 좋지 않습니다. 프론트엔드는 전체 URL을 보내고, 백엔드가 32자리 page ID를 추출하는 방식이 자연스럽습니다.

지원하면 좋은 URL 예시는 다음과 같습니다.

```text
https://www.notion.so/workspace/My-Page-3907736fa64880df9e2ee9302f483c27
https://www.notion.so/3907736fa64880df9e2ee9302f483c27
https://app.notion.com/p/Notion-3907736fa64880df9e2ee9302f483c27
```

파싱 결과:

```text
3907736fa64880df9e2ee9302f483c27
```

## 빈 경험 필터링

Notion root 페이지에는 `## 경험1`, `## 경험2`처럼 하위 페이지 링크 제목만 있는 경우가 많습니다. LLM이 이런 링크 제목을 경험으로 오인할 수 있습니다.

이를 막기 위해 `ExperienceDraft`를 저장하기 전에 제목만 있는 draft를 제거합니다. 아래 중 하나라도 있으면 의미 있는 경험으로 보고 저장합니다.

- `summary`
- `organization`
- `role`
- STAR 필드: `situation`, `task`, `action`, `result`, `learned`
- evidence excerpt
- 분류 필드: `experience_type`, `skills`, `competencies`, `keywords`

이 방식은 root 페이지에 실제 경험 내용이 있으면 저장하고, 단순 하위 페이지 링크만 있는 경우는 버립니다.

## 저장 위치

PostgreSQL 데이터는 Docker Compose에서 로컬 경로에 저장합니다.

```yaml
- ./infra/postgres/data:/var/lib/postgresql/data
```

로컬 저장 경로:

```text
infra/postgres/data
```

DB 데이터는 git에 올라가지 않도록 ignore합니다.

```gitignore
infra/postgres/data/*
```

## 주요 테이블

| 테이블 | 역할 |
| --- | --- |
| `source_documents` | 텍스트 원문, PDF에서 추출한 텍스트, Notion 페이지 텍스트를 저장합니다. |
| `experiences` | LLM이 추출한 구조화 경험 카드를 저장합니다. |
| `experience_sources` | 경험과 원문 문서의 evidence 관계를 저장합니다. |
| `experience_chunks` | RAG 검색에 사용할 경험 chunk를 저장합니다. |
| `experience_questions` | 부족한 정보를 보완하기 위한 질문을 저장합니다. |

## 프론트엔드 참고

데모 UI에서는 아래 입력 폼이 적절합니다.

```text
Notion API token
Notion page URL
Max pages
Import button
```

import 결과 화면에서는 아래 값을 보여주면 됩니다.

- 가져온 페이지 수
- 처리된 문서 수
- 추출된 경험 수
- 생성된 보완 질문 수
- 추출된 경험 제목 목록

Notion import가 권한 문제로 실패하면 다음과 같은 메시지가 적절합니다.

```text
Notion 페이지를 읽을 수 없습니다. 해당 페이지의 Add connections에서 KHU:DArchive integration을 연결했는지 확인해주세요.
```

## 운영 전환 메모

데모 흐름은 사용자가 직접 Notion internal integration token을 입력하는 방식입니다. 여러 사용자가 실제로 사용하는 서비스로 전환할 때는 Notion OAuth를 붙이고, 사용자별 access token을 안전하게 저장하는 구조로 바꾸는 것이 맞습니다.
