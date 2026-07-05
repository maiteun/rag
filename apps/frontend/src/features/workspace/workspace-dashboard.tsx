import { ExperiencePanel } from '../experiences/components/experience-panel'
import { JobDescriptionPanel } from '../matching/components/job-description-panel'
import { MatchingCanvas } from '../matching/components/matching-canvas'
import { ResumePanel } from '../resumes/components/resume-panel'
import type {
  ExperienceSummary,
  MatchResult,
  Recommendation,
  ResumeSummary,
} from '../../types'
import type { MobileView } from './use-workspace'

interface WorkspaceDashboardProps {
  experiences: ExperienceSummary[]
  resumes: ResumeSummary[]
  recommendations: Recommendation[]
  loading: boolean
  error: string
  match: MatchResult | null
  activeQuestion: number
  mobileView: MobileView
  resumeExpanded: boolean
  onQuestionChange: (index: number) => void
  onMatch: () => void
  onExperience: (id: string) => void
  onResume: (id: string) => void
  onResumeToggle: () => void
}

const dashboardBase =
  'grid min-h-0 flex-1 gap-[18px] px-9 pb-[30px] max-[1100px]:gap-3.5 max-[1100px]:px-6 max-[760px]:block max-[760px]:px-3.5 max-[760px]:pb-3.5'

export function WorkspaceDashboard(props: WorkspaceDashboardProps) {
  return props.match ? <MatchedDashboard {...props} /> : <DefaultDashboard {...props} />
}

function DefaultDashboard(props: WorkspaceDashboardProps) {
  return (
    <div
      className={`${dashboardBase} grid-cols-[minmax(260px,.88fr)_minmax(420px,1.45fr)_minmax(250px,.84fr)] max-[1100px]:grid-cols-[minmax(230px,.8fr)_minmax(380px,1.25fr)] ${mobileVisibility(props.mobileView)}`}
    >
      <ExperiencePanel
        experiences={props.experiences}
        recommendations={props.recommendations}
        loading={props.loading}
        error={props.error}
        onOpen={props.onExperience}
      />
      <MatchingCanvas
        match={null}
        activeQuestion={props.activeQuestion}
        onQuestionChange={props.onQuestionChange}
        onStart={props.onMatch}
        onExperience={props.onExperience}
      />
      <ResumePanel resumes={props.resumes} onOpen={props.onResume} />
    </div>
  )
}

function MatchedDashboard(props: WorkspaceDashboardProps & { match: MatchResult | null }) {
  if (!props.match) return null

  const sourceRows = props.resumeExpanded
    ? 'grid-rows-[minmax(0,1fr)_minmax(0,1fr)]'
    : 'grid-rows-[minmax(0,1fr)_58px]'

  return (
    <div
      className={`${dashboardBase} grid-cols-[minmax(280px,.92fr)_minmax(440px,1.45fr)_minmax(270px,.88fr)] max-[1100px]:grid-cols-[minmax(230px,.8fr)_minmax(380px,1.25fr)] ${matchedMobileVisibility(props.mobileView)}`}
    >
      <div
        className={`source-stack grid min-h-0 gap-[18px] transition-[grid-template-rows] duration-250 max-[1100px]:[&_.resume-column]:flex ${sourceRows}`}
      >
        <ExperiencePanel
          experiences={props.experiences}
          recommendations={props.recommendations}
          loading={props.loading}
          error={props.error}
          onOpen={props.onExperience}
        />
        <ResumePanel
          resumes={props.resumes}
          onOpen={props.onResume}
          collapsible
          expanded={props.resumeExpanded}
          onToggle={props.onResumeToggle}
        />
      </div>
      <MatchingCanvas
        match={props.match}
        activeQuestion={props.activeQuestion}
        onQuestionChange={props.onQuestionChange}
        onStart={props.onMatch}
        onExperience={props.onExperience}
      />
      <JobDescriptionPanel match={props.match} />
    </div>
  )
}

function mobileVisibility(view: MobileView) {
  return {
    experiences: 'max-[760px]:[&_.experience-column]:flex',
    matching: 'max-[760px]:[&_.matching-column]:flex',
    resumes: 'max-[760px]:[&_.resume-column]:flex',
  }[view]
}

function matchedMobileVisibility(view: MobileView) {
  return {
    experiences:
      'max-[760px]:[&_.source-stack]:grid max-[760px]:[&_.source-stack]:h-full max-[760px]:[&_.experience-column]:flex',
    matching: 'max-[760px]:[&_.source-stack]:hidden max-[760px]:[&_.matching-column]:flex',
    resumes:
      'max-[760px]:[&_.source-stack]:grid max-[760px]:[&_.source-stack]:h-full max-[760px]:[&_.source-stack]:grid-rows-[0_minmax(0,1fr)] max-[760px]:[&_.resume-column]:flex',
  }[view]
}
