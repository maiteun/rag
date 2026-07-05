import { TagList } from '../../../components/ui/tag-list'
import { PanelHeader, PanelMessage, PanelSkeleton } from '../../../components/ui/panel'
import { MatchLevelChip } from '../../../components/ui/match-level-chip'
import type { ExperienceSummary, Recommendation } from '../../../types'

interface ExperiencePanelProps {
  experiences: ExperienceSummary[]
  recommendations: Recommendation[]
  loading: boolean
  error: string
  onOpen: (id: string) => void
}

export function ExperiencePanel({
  experiences,
  recommendations,
  loading,
  error,
  onOpen,
}: ExperiencePanelProps) {
  const recommendationMap = new Map(
    recommendations.map((item) => [item.experienceId, item]),
  )
  const recommended = recommendations
    .map((item) => experiences.find((experience) => experience.id === item.experienceId))
    .filter((item): item is ExperienceSummary => Boolean(item))
  const others = experiences.filter((item) => !recommendationMap.has(item.id))

  return (
    <section className="experience-column flex min-h-0 flex-col overflow-hidden rounded-[14px] bg-panel max-[760px]:hidden max-[760px]:h-full">
      <PanelHeader title="경험" count={experiences.length} />
      <div className="min-h-0 overflow-auto px-3.5 pb-4 [overscroll-behavior:contain] [scrollbar-width:thin]">
        <ExperienceList
          experiences={experiences}
          recommended={recommended}
          others={others}
          recommendationMap={recommendationMap}
          loading={loading}
          error={error}
          onOpen={onOpen}
        />
      </div>
    </section>
  )
}

interface ExperienceListProps extends Omit<ExperiencePanelProps, 'recommendations'> {
  recommended: ExperienceSummary[]
  others: ExperienceSummary[]
  recommendationMap: Map<string, Recommendation>
}

function ExperienceList({
  experiences,
  recommended,
  others,
  recommendationMap,
  loading,
  error,
  onOpen,
}: ExperienceListProps) {
  if (loading) return <PanelSkeleton />
  if (error) return <PanelMessage>{error}</PanelMessage>
  if (!experiences.length) return <PanelMessage>등록된 경험이 없습니다.</PanelMessage>

  return (
    <>
      {recommended.length > 0 && (
        <div>
          <h3 className="mx-0.5 mt-0 mb-[9px] text-[12px] tracking-[.3px] text-[#797b85]">
            추천 경험
          </h3>
          {recommended.map((item) => (
            <ExperienceCard
              key={item.id}
              item={item}
              recommendation={recommendationMap.get(item.id)}
              onOpen={onOpen}
            />
          ))}
        </div>
      )}
      {recommended.length > 0 && others.length > 0 && <GroupSeparator />}
      {others.map((item) => (
        <ExperienceCard key={item.id} item={item} onOpen={onOpen} />
      ))}
    </>
  )
}

function GroupSeparator() {
  return (
    <div className="my-[17px] mx-0.5 flex items-center gap-2 text-[10px] text-[#90919a] before:flex-1 before:border-t before:border-dashed before:border-[#c9cad0] before:content-[''] after:flex-1 after:border-t after:border-dashed after:border-[#c9cad0] after:content-['']">
      <span>그 외 경험</span>
    </div>
  )
}

interface ExperienceCardProps {
  item: ExperienceSummary
  recommendation?: Recommendation
  onOpen: (id: string) => void
}

function ExperienceCard({ item, recommendation, onOpen }: ExperienceCardProps) {
  return (
    <button
      className="mb-[11px] block w-full rounded-[11px] bg-white p-[15px] text-left transition-shadow duration-350 hover:shadow-[0_0_12px_rgba(30,35,60,.10)]"
      onClick={() => onOpen(item.id)}
    >
      <div className="flex items-center gap-1.5">
        {recommendation && (
          <span className="inline-flex size-6 shrink-0 items-center justify-center rounded-md bg-brand text-[11px] font-extrabold text-white">
            {recommendation.rank}
          </span>
        )}
        <strong className="flex-1 text-sm leading-[1.35]">{item.title}</strong>
        {recommendation && <MatchLevelChip level={recommendation.matchLevel} />}
      </div>
      <p className="my-2 line-clamp-3 text-[13px] leading-[1.55] text-muted">
        {recommendation?.reason || item.summary}
      </p>
      <TagList items={item.skills.slice(0, 3)} />
    </button>
  )
}
