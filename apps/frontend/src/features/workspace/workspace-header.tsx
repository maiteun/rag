import { Icon } from '../../components/ui/icon'
import type { MatchResult } from '../../types'

interface WorkspaceHeaderProps {
  match: MatchResult | null
  experienceCount: number
  resumeCount: number
  onMatch: () => void
}

export function WorkspaceHeader({
  match,
  experienceCount,
  resumeCount,
  onMatch,
}: WorkspaceHeaderProps) {
  return (
    <>
      <header className="flex h-[72px] shrink-0 items-center justify-end border-b border-line px-[34px] max-[1100px]:px-6 max-[760px]:hidden">
        <div className="flex items-center gap-[18px]">
          <span className="text-xs text-muted">
            {match ? '최근 매칭 완료' : ''}
          </span>
          <button
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-brand px-4 py-[11px] text-sm font-bold text-white hover:bg-brand-dark"
            onClick={onMatch}
          >
            <Icon name="sparkle" size={18} />
            매칭 시작
          </button>
        </div>
      </header>

      <div className="flex shrink-0 items-end justify-between px-9 pt-7 pb-6 max-[1100px]:px-6 max-[760px]:items-start max-[760px]:p-5">
        <div>
          <h1 className="mt-0 text-[30px] font-semibold tracking-[-1.2px] max-[760px]:text-2xl">
            {match ? getMatchTitle(match) : '자소서 작업대'}
          </h1>
          <span className="text-sm text-muted max-[760px]:hidden">
            {match
              ? '문항별 추천 경험과 근거를 확인하세요.'
              : '경험과 이력서를 살펴보고 문항에 맞는 경험을 찾아보세요.'}
          </span>
        </div>
        <div className="flex gap-[9px] max-[760px]:hidden">
          <Stat count={experienceCount} label="경험" />
          <Stat count={resumeCount} label="이력서" />
        </div>
      </div>
    </>
  )
}

function getMatchTitle(match: MatchResult) {
  const company = match.company || '지원 기업'
  return match.role ? `${company} · ${match.role}` : company
}

function Stat({ count, label }: { count: number; label: string }) {
  return (
    <span className="min-w-[72px] rounded-lg bg-[#f5f5f7] px-3 py-2.5 text-xs text-muted">
      <strong className="mb-[3px] block text-[17px] text-ink">{count}</strong>
      {label}
    </span>
  )
}
