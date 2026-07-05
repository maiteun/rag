import { PanelHeader } from '../../../components/ui/panel'
import { TagList } from '../../../components/ui/tag-list'
import type { MatchResult } from '../../../types'

export function JobDescriptionPanel({ match }: { match: MatchResult }) {
  return (
    <section className="jd-column flex min-h-0 flex-col overflow-hidden rounded-[14px] bg-panel max-[1100px]:hidden max-[760px]:h-full">
      <PanelHeader title="채용 공고" />
      <div className="min-h-0 overflow-auto px-[18px] pb-5">
        <JobSection label="지원 정보" first>
          <h3 className="mt-0 mb-[5px] text-lg">{match.company || '지원 기업'}</h3>
          {match.role && <BodyText>{match.role}</BodyText>}
        </JobSection>

        {match.jobAnalysis && (
          <JobSection label="직무 요약">
            <BodyText>{match.jobAnalysis.summary}</BodyText>
          </JobSection>
        )}

        {match.jobAnalysis && (
          <JobSection label="핵심 요구 역량">
            <TagList
              items={[
                ...match.jobAnalysis.requiredSkills,
                ...match.jobAnalysis.competencies,
              ]}
              tone="blue"
            />
          </JobSection>
        )}

        <JobSection label="JD 원문">
          <BodyText className="whitespace-pre-wrap">{match.jobDescription}</BodyText>
        </JobSection>
      </div>
    </section>
  )
}

function JobSection({
  label,
  first = false,
  children,
}: {
  label: string
  first?: boolean
  children: React.ReactNode
}) {
  return (
    <section className={`${first ? 'pt-1.5' : 'border-t border-[#e1e2e6] pt-[18px]'} pb-[18px]`}>
      <span className="mb-[9px] block text-[12px] font-extrabold">{label}</span>
      {children}
    </section>
  )
}

function BodyText({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return <p className={`m-0 text-[13px] leading-[1.7] text-[#555762] ${className}`}>{children}</p>
}
