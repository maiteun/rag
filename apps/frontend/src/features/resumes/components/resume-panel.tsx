import { Icon } from '../../../components/ui/icon'
import { PanelHeader, PanelMessage } from '../../../components/ui/panel'
import type { ResumeSummary } from '../../../types'

interface ResumePanelProps {
  resumes: ResumeSummary[]
  onOpen: (id: string) => void
  collapsible?: boolean
  expanded?: boolean
  onToggle?: () => void
}

export function ResumePanel({
  resumes,
  onOpen,
  collapsible = false,
  expanded = true,
  onToggle,
}: ResumePanelProps) {
  return (
    <section className="resume-column flex min-h-0 flex-col overflow-hidden rounded-[14px] bg-panel max-[1100px]:hidden max-[760px]:h-full">
      {collapsible ? (
        <ResumeToggle count={resumes.length} expanded={expanded} onToggle={onToggle} />
      ) : (
        <>
          <PanelHeader title="과거 이력서" count={resumes.length} tone="sky" />
        </>
      )}

      {expanded && <ResumeList resumes={resumes} onOpen={onOpen} />}
    </section>
  )
}

function ResumeToggle({
  count,
  expanded,
  onToggle,
}: {
  count: number
  expanded: boolean
  onToggle?: () => void
}) {
  return (
    <button
      className="flex h-[58px] shrink-0 items-center justify-between bg-transparent px-[18px]"
      onClick={onToggle}
    >
      <span className="flex items-center gap-2">
        <strong className="text-sm">과거 이력서</strong>
        <span className="inline-flex h-5 min-w-5 items-center justify-center rounded-full bg-[#e6e7eb] text-[10px] text-[#757782]">
          {count}
        </span>
      </span>
      <span
        className={`text-[#777a85] transition-transform duration-200 ${
          expanded ? 'rotate-180' : ''
        }`}
      >
        <Icon name="chevron" />
      </span>
    </button>
  )
}

function ResumeList({ resumes, onOpen }: Pick<ResumePanelProps, 'resumes' | 'onOpen'>) {
  return (
    <div className="min-h-0 overflow-auto px-3.5 pb-4 [overscroll-behavior:contain] [scrollbar-width:thin]">
      {resumes.length ? (
        resumes.map((resume, index) => (
          <ResumeCard
            key={resume.id}
            resume={resume}
            index={index}
            onOpen={onOpen}
          />
        ))
      ) : (
        <PanelMessage>등록된 이력서가 없습니다.</PanelMessage>
      )}
    </div>
  )
}

function ResumeCard({
  resume,
  index,
  onOpen,
}: {
  resume: ResumeSummary
  index: number
  onOpen: (id: string) => void
}) {
  return (
    <button
      className="mb-[11px] grid w-full grid-cols-[auto_1fr_auto] items-center gap-3 rounded-[11px] bg-white p-[15px] text-left transition-shadow duration-350 hover:shadow-[0_0_12px_rgba(30,35,60,.10)]"
      onClick={() => onOpen(resume.id)}
    >
      <span className="flex size-9 items-center justify-center rounded-lg bg-brand-soft text-[12px] font-extrabold text-brand">
        {String(index + 1).padStart(2, '0')}
      </span>
      <span className="min-w-0">
        <strong className="block text-sm leading-[1.4]">{resume.title}</strong>
        <span className="my-0.5 block truncate text-[12px] text-[#7e808a]">
          {resume.fileName || '텍스트 이력서'}
        </span>
        <small className="block text-[12px] text-[#a0a2aa]">
          {new Date(resume.createdAt).toLocaleDateString('ko-KR')}
          {resume.experienceCount != null && ` · 경험 ${resume.experienceCount}개`}
        </small>
      </span>
    </button>
  )
}
