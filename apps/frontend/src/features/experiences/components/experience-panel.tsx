import type { DragEvent } from 'react'
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
  draggable?: boolean
  draggedExperienceId?: string | null
  onDragStart?: (id: string) => void
  onDragEnd?: () => void
}

export function ExperiencePanel({
  experiences,
  recommendations,
  loading,
  error,
  onOpen,
  draggable = false,
  draggedExperienceId,
  onDragStart,
  onDragEnd,
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
          draggable={draggable}
          draggedExperienceId={draggedExperienceId}
          onDragStart={onDragStart}
          onDragEnd={onDragEnd}
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
  draggable,
  draggedExperienceId,
  onDragStart,
  onDragEnd,
}: ExperienceListProps) {
  if (loading) return <PanelSkeleton />
  if (error) return <PanelMessage>{error}</PanelMessage>
  if (!experiences.length) return <PanelMessage>등록된 경험이 없습니다.</PanelMessage>

  return (
    <>
      {recommended.length > 0 && (
        <div>
          <h3 className="mx-0.5 mt-0 mb-[9px] text-[13px] tracking-[.3px] text-[#797b85]">
            추천 경험
          </h3>
          {recommended.map((item) => (
            <ExperienceCard
              key={item.id}
              item={item}
              recommendation={recommendationMap.get(item.id)}
              onOpen={onOpen}
              draggable={draggable}
              isDragging={draggedExperienceId === item.id}
              onDragStart={onDragStart}
              onDragEnd={onDragEnd}
            />
          ))}
        </div>
      )}
      {recommended.length > 0 && others.length > 0 && <GroupSeparator />}
      {others.map((item) => (
        <ExperienceCard
          key={item.id}
          item={item}
          onOpen={onOpen}
          draggable={draggable}
          isDragging={draggedExperienceId === item.id}
          onDragStart={onDragStart}
          onDragEnd={onDragEnd}
        />
      ))}
    </>
  )
}

function GroupSeparator() {
  return (
    <div className="my-[17px] mx-0.5 flex items-center gap-2 text-[13px] text-[#797b85] before:flex-1 before:border-t before:border-dashed before:border-[#c9cad0] before:content-[''] after:flex-1 after:border-t after:border-dashed after:border-[#c9cad0] after:content-['']">
      <span>그 외 경험</span>
    </div>
  )
}

interface ExperienceCardProps {
  item: ExperienceSummary
  recommendation?: Recommendation
  onOpen: (id: string) => void
  draggable?: boolean
  isDragging?: boolean
  onDragStart?: (id: string) => void
  onDragEnd?: () => void
}

function ExperienceCard({
  item,
  recommendation,
  onOpen,
  draggable = false,
  isDragging = false,
  onDragStart,
  onDragEnd,
}: ExperienceCardProps) {
  const cardClass = isDragging
    ? 'border-2 border-dashed border-brand bg-brand-soft shadow-none'
    : 'border-2 border-transparent bg-white hover:shadow-[0_0_12px_rgba(30,35,60,.10)]'

  const startDragging = (event: DragEvent<HTMLButtonElement>) => {
    if (!draggable) {
      event.preventDefault()
      return
    }

    event.dataTransfer.effectAllowed = 'move'
    event.dataTransfer.setData('text/plain', item.id)
    setDragPreview(event)
    onDragStart?.(item.id)
  }

  return (
    <button
      className={`mb-[11px] block w-full rounded-[11px] p-[13px] text-left transition-[background-color,border-color,box-shadow] duration-200 ${cardClass}`}
      draggable={draggable}
      onDragStart={startDragging}
      onDragEnd={onDragEnd}
      onClick={() => onOpen(item.id)}
    >
      <div className={isDragging ? 'invisible' : ''}>
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
      </div>
    </button>
  )
}

function setDragPreview(event: DragEvent<HTMLButtonElement>) {
  const preview = event.currentTarget.cloneNode(true) as HTMLButtonElement
  const { width } = event.currentTarget.getBoundingClientRect()

  preview.style.position = 'fixed'
  preview.style.top = '-1000px'
  preview.style.left = '-1000px'
  preview.style.width = `${width}px`
  preview.style.boxShadow = '0 18px 42px rgba(30, 35, 60, 0.28)'
  preview.style.background = '#fff'
  preview.style.borderColor = 'transparent'
  document.body.appendChild(preview)
  event.dataTransfer.setDragImage(preview, 24, 24)
  requestAnimationFrame(() => preview.remove())
}
