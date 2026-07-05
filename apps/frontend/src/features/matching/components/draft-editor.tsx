import { useState, type DragEvent } from 'react'
import { Icon } from '../../../components/ui/icon'
import type { ExperienceSummary } from '../../../types'

interface DraftEditorProps {
  selectedExperiences: ExperienceSummary[]
  generated: boolean
  value: string
  loading: boolean
  error?: string
  onDropExperience: (id: string) => void
  onRemoveExperience: (id: string) => void
  onChange: (value: string) => void
  onGenerate: () => void
}

export function DraftEditor({
  selectedExperiences,
  generated,
  value,
  loading,
  error,
  onDropExperience,
  onRemoveExperience,
  onChange,
  onGenerate,
}: DraftEditorProps) {
  const [dragOver, setDragOver] = useState(false)

  const dropExperience = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    setDragOver(false)
    const experienceId = event.dataTransfer.getData('text/plain')
    if (experienceId) onDropExperience(experienceId)
  }

  return (
    <section className="flex min-h-0 flex-1 flex-col pb-4">
      <div className="mb-2 flex shrink-0 items-end justify-between">
        <span className="text-[13px] text-[#797b85]">
          {generated ? '자기소개서 초안' : '초안에 사용할 경험'}
        </span>
        <button
          className="rounded-md bg-brand px-3 py-1.5 text-xs font-bold text-white hover:bg-brand-dark disabled:cursor-not-allowed disabled:bg-[#abb2c8]"
          disabled={loading || selectedExperiences.length === 0}
          onClick={onGenerate}
        >
          {loading ? '작성 중…' : generated ? '다시 작성' : '초안 작성'}
        </button>
      </div>

      {generated ? (
        <textarea
          aria-label="자기소개서 초안"
          className="min-h-[180px] flex-1 resize-none rounded-[10px] border border-[#dfe0e4] bg-white p-3 text-[13px] leading-[1.65] outline-none focus:border-brand focus:shadow-[0_0_0_3px_rgba(23,70,245,.08)]"
          value={value}
          onChange={(event) => onChange(event.target.value)}
        />
      ) : (
        <div
          className={`min-h-[180px] flex-1 overflow-auto rounded-[12px] border-2 border-dashed p-3 transition-colors ${
            dragOver
              ? 'border-brand bg-brand-soft'
              : 'border-[#cfd1d8] bg-white'
          }`}
          onDragEnter={(event) => {
            event.preventDefault()
            setDragOver(true)
          }}
          onDragOver={(event) => {
            event.preventDefault()
            event.dataTransfer.dropEffect = 'move'
          }}
          onDragLeave={(event) => {
            if (!event.currentTarget.contains(event.relatedTarget as Node)) {
              setDragOver(false)
            }
          }}
          onDrop={dropExperience}
        >
          {selectedExperiences.length ? (
            <div className="grid gap-2.5">
              {selectedExperiences.map((experience) => (
                <SelectedExperienceBlock
                  key={experience.id}
                  experience={experience}
                  onRemove={onRemoveExperience}
                />
              ))}
            </div>
          ) : (
            <div className="flex h-full min-h-[150px] items-center justify-center px-6 text-center text-[13px] leading-[1.6] text-[#8b8d97]">
              왼쪽의 경험 카드를 이곳으로 드래그하세요.
            </div>
          )}
        </div>
      )}

      {error && <p className="mt-1.5 mb-0 text-[11px] text-[#cf3434]">{error}</p>}
    </section>
  )
}

function SelectedExperienceBlock({
  experience,
  onRemove,
}: {
  experience: ExperienceSummary
  onRemove: (id: string) => void
}) {
  return (
    <article className="relative rounded-[10px] bg-[#f4f5f7] p-3 pr-10">
      <strong className="block text-sm leading-[1.4]">{experience.title}</strong>
      <p className="mt-1.5 mb-0 line-clamp-2 text-xs leading-[1.55] text-muted">
        {experience.summary}
      </p>
      <button
        className="absolute top-2 right-2 rounded-md bg-transparent p-1.5 text-[#777a85] hover:bg-white hover:text-ink"
        aria-label={`${experience.title} 제거`}
        onClick={() => onRemove(experience.id)}
      >
        <Icon name="close" size={16} />
      </button>
    </article>
  )
}
