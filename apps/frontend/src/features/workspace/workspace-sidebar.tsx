import { Icon } from '../../components/ui/icon'
import type { MobileView } from './use-workspace'

interface WorkspaceSidebarProps {
  activeView: MobileView
  onHome: () => void
  onViewChange: (view: MobileView) => void
  onMatch: () => void
}

export function WorkspaceSidebar({
  activeView,
  onHome,
  onViewChange,
  onMatch,
}: WorkspaceSidebarProps) {
  return (
    <aside className="flex min-h-0 flex-col rounded-l-[18px] border border-line bg-white px-[18px] pt-[25px] pb-[18px] max-[760px]:h-[62px] max-[760px]:flex-row max-[760px]:rounded-none max-[760px]:border-0 max-[760px]:border-b max-[760px]:px-[15px] max-[760px]:py-0">
      <button
        className="mx-2 mb-[30px] flex items-center bg-transparent p-0 text-xl font-extrabold tracking-[-.6px] max-[760px]:mr-auto max-[760px]:mb-0 max-[760px]:ml-0"
        onClick={onHome}
      >
        <span className="mr-2 inline-flex size-[25px] -rotate-[8deg] items-center justify-center rounded-[5px] bg-brand text-sm text-white">
          ㅁ
        </span>
        모람
      </button>

      <nav className="grid gap-[5px] max-[760px]:flex max-[760px]:gap-0.5">
        <NavButton icon="home" label="홈" onClick={onHome} mobileHidden />
        <NavButton
          icon="archive"
          label="경험"
          active={activeView === 'experiences'}
          onClick={() => onViewChange('experiences')}
        />
        <NavButton
          icon="sparkle"
          label="문항 매칭"
          active={activeView === 'matching'}
          onClick={() => onViewChange('matching')}
        />
        <NavButton
          icon="file"
          label="과거 이력서"
          active={activeView === 'resumes'}
          onClick={() => onViewChange('resumes')}
        />
      </nav>

      <MatchGuide onMatch={onMatch} />
      <WorkspaceProfile />
    </aside>
  )
}

function NavButton({
  icon,
  label,
  active = false,
  mobileHidden = false,
  onClick,
}: {
  icon: 'home' | 'archive' | 'sparkle' | 'file'
  label: string
  active?: boolean
  mobileHidden?: boolean
  onClick: () => void
}) {
  return (
    <button
      className={`flex items-center gap-3 rounded-lg px-3 py-[11px] text-left text-sm hover:bg-[#f5f5f7] hover:text-ink max-[760px]:gap-0 max-[760px]:p-[11px] ${
        active ? 'bg-[#f4f5f7] font-bold' : 'bg-transparent text-[#666977]'
      } ${mobileHidden ? 'max-[760px]:hidden' : ''}`}
      onClick={onClick}
    >
      <Icon name={icon} />
      <span className="max-[760px]:hidden">{label}</span>
    </button>
  )
}

function MatchGuide({ onMatch }: { onMatch: () => void }) {
  return (
    <div className="mt-auto flex flex-col items-center rounded-[14px] bg-[#f4f5f7] px-3.5 py-5 text-center max-[760px]:hidden">
      <span className="mb-[13px] flex size-[42px] items-center justify-center rounded-full bg-white text-brand">
        <Icon name="sparkle" />
      </span>
      <strong className="text-[13px]">경험에서 답을 찾으세요.</strong>
      <p className="my-2 mb-3.5 text-xs leading-normal text-muted">
        JD와 문항을 입력하면 적합한 경험을 추천합니다.
      </p>
      <button
        className="w-full rounded-[7px] border border-[#dedfe3] bg-white px-[13px] py-[9px] text-xs font-bold"
        onClick={onMatch}
      >
        매칭 시작
      </button>
    </div>
  )
}

function WorkspaceProfile() {
  return (
    <footer className="mt-[18px] grid grid-cols-[auto_1fr_auto] items-center gap-[9px] border-t border-line px-[5px] pt-[17px] max-[760px]:hidden">
      <span className="flex size-[34px] items-center justify-center rounded-full bg-[#20222b] text-[11px] text-white">
        나
      </span>
      <span>
        <strong className="block text-xs">내 아카이브</strong>
        <small className="mt-[2px] block text-xs text-[#999ba5]">개인 워크스페이스</small>
      </span>
    </footer>
  )
}
