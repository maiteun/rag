import { ExperienceDetailModal } from '../experiences/components/experience-detail-modal'
import { MatchCreateModal } from '../matching/components/match-create-modal'
import { MatchStatusModal } from '../matching/components/match-status-modal'
import { ResumeDetailModal } from '../resumes/components/resume-detail-modal'
import { useWorkspace, type MobileView } from './use-workspace'
import { WorkspaceDashboard } from './workspace-dashboard'
import { WorkspaceHeader } from './workspace-header'
import { WorkspaceSidebar } from './workspace-sidebar'

interface WorkspacePageProps {
  initialMatchingOpen: boolean
  onHome: () => void
}

export function WorkspacePage({ initialMatchingOpen, onHome }: WorkspacePageProps) {
  const workspace = useWorkspace(initialMatchingOpen)

  const changeMobileView = (view: MobileView) => {
    workspace.setMobileView(view)
    if (view === 'resumes') workspace.setResumeExpanded(true)
  }

  const closeExperience = () => workspace.setExperienceDetail(null)
  const closeResume = () => workspace.setResumeDetail(null)

  const openResumeFromExperience = (id: string) => {
    closeExperience()
    void workspace.openResume(id)
  }

  const openExperienceFromResume = (id: string) => {
    closeResume()
    void workspace.openExperience(id)
  }

  return (
    <div className="grid h-dvh grid-cols-[230px_minmax(0,1fr)] overflow-hidden bg-page p-[18px] max-[1100px]:grid-cols-[195px_minmax(0,1fr)] max-[1100px]:p-2.5 max-[760px]:block max-[760px]:p-0">
      <WorkspaceSidebar
        activeView={workspace.mobileView}
        onHome={onHome}
        onViewChange={changeMobileView}
        onMatch={() => workspace.setMatchModalOpen(true)}
      />

      <main className="flex min-w-0 flex-col overflow-hidden rounded-r-[18px] border border-l-0 border-line bg-white max-[760px]:h-[calc(100dvh-62px)] max-[760px]:rounded-none max-[760px]:border-0">
        <WorkspaceHeader
          match={workspace.match}
          onMatch={() => workspace.setMatchModalOpen(true)}
        />
        <WorkspaceDashboard
          experiences={workspace.experiences}
          resumes={workspace.resumes}
          recommendations={workspace.recommendations}
          loading={workspace.loading}
          error={workspace.error}
          match={workspace.match}
          activeQuestion={workspace.activeQuestion}
          mobileView={workspace.mobileView}
          resumeExpanded={workspace.resumeExpanded}
          onQuestionChange={workspace.setActiveQuestion}
          onMatch={() => workspace.setMatchModalOpen(true)}
          onExperience={(id) => void workspace.openExperience(id)}
          onResume={(id) => void workspace.openResume(id)}
          onResumeToggle={() => workspace.setResumeExpanded((value) => !value)}
        />
      </main>

      {workspace.matchModalOpen && (
        <MatchCreateModal
          initialValue={workspace.matchInput}
          onClose={() => workspace.setMatchModalOpen(false)}
          onSubmit={workspace.submitMatch}
        />
      )}

      {workspace.matchStatus && (
        <MatchStatusModal
          status={workspace.matchStatus}
          error={workspace.matchError}
          onClose={workspace.closeMatchStatus}
          onRetry={workspace.retryMatch}
        />
      )}

      {(workspace.experienceLoading || workspace.experienceDetail) && (
        <ExperienceDetailModal
          data={workspace.experienceDetail}
          loading={workspace.experienceLoading}
          onClose={closeExperience}
          onResume={openResumeFromExperience}
        />
      )}

      {(workspace.resumeLoading || workspace.resumeDetail) && (
        <ResumeDetailModal
          data={workspace.resumeDetail}
          loading={workspace.resumeLoading}
          experiences={workspace.experiences}
          onClose={closeResume}
          onExperience={openExperienceFromResume}
        />
      )}
    </div>
  )
}
