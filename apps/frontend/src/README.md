# 모람 프런트엔드 구조

기능 코드는 `features`에서 찾고, 애플리케이션 조립은 `app`에서 담당한다.

```text
src/
├─ app/                  # 최상위 화면 조립과 진입 흐름
├─ components/ui/        # 여러 기능에서 공유하는 작은 UI
├─ features/
│  ├─ landing/           # 초기 화면
│  ├─ experiences/       # 경험 목록과 상세
│  ├─ matching/          # 매칭 입력, 상태, 결과
│  ├─ resumes/           # 이력서 목록과 상세
│  └─ workspace/         # 기능 블록을 조립하는 작업대
├─ api/                  # 실제 API와 mock을 정규화하는 데이터 계층
├─ mocks/                # 로컬 실행용 fixture
└─ types.ts              # API와 기능이 공유하는 도메인 타입
```

## 자주 수정할 위치

- 전역 색상 토큰, 폰트, 애니메이션: `index.css`
- 컴포넌트 스타일: 각 컴포넌트의 Tailwind `className`
- 랜딩 화면: `features/landing/landing-page.tsx`
- 작업대 배치: `features/workspace/workspace-dashboard.tsx`
- 작업대 상태와 API 호출: `features/workspace/use-workspace.ts`
- 경험 카드: `features/experiences/components/experience-panel.tsx`
- 매칭 결과: `features/matching/components/matching-canvas.tsx`
- 모달 공통 크기와 구조: `components/ui/modal.tsx`

의존성 방향은 `components/api/types → features → app`으로 유지한다. 한 feature가 다른 feature의 내부 컴포넌트를 직접 가져오기보다 `workspace` 또는 `app`에서 조립한다.
