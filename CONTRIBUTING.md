# Contributing

## Commit Message

이 저장소의 커밋 메시지는 다음 형식을 사용합니다.

```text
type(scope): subject
```

예시:

```text
feat(backend): webhook 수신 어댑터 추가
chore: gitignore에 build 산출물 추가
fix(frontend): 로그인 실패 시 에러 메시지 표시
docs(api): 인증 응답 예시 추가
```

## 작성 규칙

- `type`은 커밋의 변경 목적을 나타내며 반드시 지정합니다.
- `scope`는 변경 대상 영역을 나타냅니다. 변경 범위가 명확하면 반드시 지정합니다.
- 여러 영역에 걸친 단순 설정 변경처럼 scope가 애매하면 생략할 수 있습니다.
- `subject`는 변경 내용을 짧고 구체적으로 작성합니다.
- subject 끝에는 마침표를 붙이지 않습니다.
- 한 커밋에는 하나의 목적만 담습니다.

## Type

| type | 사용 시점 |
| --- | --- |
| `feat` | 새로운 기능을 추가할 때 |
| `fix` | 버그를 수정할 때 |
| `docs` | 문서만 변경할 때 |
| `style` | 포맷팅, 세미콜론, 공백 등 동작에 영향이 없는 코드 스타일 변경 |
| `refactor` | 기능 변화 없이 코드 구조를 개선할 때 |
| `perf` | 성능을 개선할 때 |
| `test` | 테스트를 추가하거나 수정할 때 |
| `build` | 빌드 시스템, 패키지 매니저, 의존성 설정을 변경할 때 |
| `ci` | CI 설정이나 워크플로를 변경할 때 |
| `chore` | 소스나 테스트와 직접 관련 없는 기타 작업 |
| `revert` | 이전 커밋을 되돌릴 때 |

## Scope

scope는 변경된 코드나 문서의 주요 위치를 기준으로 작성합니다.

| scope | 대상 |
| --- | --- |
| `backend` | `apps/backend` |
| `frontend` | `apps/frontend` |
| `api-client` | `packages/api-client` |
| `infra` | `infra`, Docker, 배포 및 로컬 인프라 설정 |
| `db` | 데이터베이스 스키마, 마이그레이션, seed 데이터 |
| `ai` | 프롬프트, LLM, 임베딩, AI 파이프라인 |
| `api` | API 명세, 요청/응답 계약, OpenAPI 문서 |
| `docs` | `docs` 또는 프로젝트 문서 |
| `config` | lint, formatter, tsconfig, pytest 등 공통 설정 |
| `deps` | 의존성 추가, 제거, 버전 변경 |
| `repo` | 저장소 루트 설정, gitignore, 공통 스크립트 |

필요한 scope가 위 목록에 없으면, 변경 대상이 명확히 드러나는 짧은 소문자 이름을 사용합니다.

## Subject

subject는 다음 기준으로 작성합니다.

- 50자 안팎으로 작성합니다.
- "무엇을 바꿨는지"가 드러나게 작성합니다.
- 너무 넓은 표현은 피합니다.

좋은 예:

```text
feat(backend): 경험 추출 API 추가
fix(db): pgvector 확장 초기화 누락 수정
docs(development): 로컬 실행 절차 갱신
chore(repo): gitignore에 build 산출물 추가
```

피할 예:

```text
feat: 작업함
fix: 버그 수정
docs: 문서 업데이트
chore(repo): 이것저것 정리
```

## Body

본문은 선택 사항입니다. 다음 내용이 필요할 때만 작성합니다.

- 변경 이유
- 구현 방식의 중요한 결정
- 리뷰어가 알아야 할 영향 범위
- 마이그레이션이나 배포 시 주의사항

형식:

```text
feat(backend): webhook 수신 어댑터 추가

외부 서비스 이벤트를 내부 작업 큐로 전달하기 위해 webhook 엔드포인트를 추가했습니다.
서명 검증은 후속 커밋에서 처리합니다.
```

## Breaking Change

호환되지 않는 변경이 있으면 `!`를 붙이고 본문에 `BREAKING CHANGE:`를 작성합니다.

```text
feat(api)!: 경험 추천 응답 구조 변경

BREAKING CHANGE: recommendations 필드가 배열에서 객체로 변경되었습니다.
```

## Revert

되돌리기 커밋은 `revert` type을 사용합니다.

```text
revert: feat(backend): webhook 수신 어댑터 추가
```
