import { useState } from 'react'
import { Icon } from '../../../components/ui/icon'
import { PanelHeader } from '../../../components/ui/panel'
import { createCoverLetterDraft } from '../../../api/data-source'
import { DraftEditor } from './draft-editor'
import type { ExperienceSummary, MatchResult } from '../../../types'

interface MatchingCanvasProps {
  match: MatchResult | null
  experiences: ExperienceSummary[]
  activeQuestion: number
  onQuestionChange: (index: number) => void
  onStart: () => void
}

export function MatchingCanvas({
  match,
  experiences,
  activeQuestion,
  onQuestionChange,
  onStart,
}: MatchingCanvasProps) {
  const question = match?.questions[activeQuestion]
  const [drafts, setDrafts] = useState<Record<string, string>>({})
  const [draftErrors, setDraftErrors] = useState<Record<string, string>>({})
  const [selectedExperienceIds, setSelectedExperienceIds] = useState<
    Record<string, string[]>
  >({})
  const [generatedQuestions, setGeneratedQuestions] = useState<
    Record<string, boolean>
  >({})
  const [generatingQuestionId, setGeneratingQuestionId] = useState<string | null>(null)

  const currentDraft = question
    ? (drafts[question.id] ?? question.draft ?? '')
    : ''
  const currentExperienceIds = question
    ? (selectedExperienceIds[question.id] ?? [])
    : []
  const currentExperiences = currentExperienceIds
    .map((id) => experiences.find((experience) => experience.id === id))
    .filter((experience): experience is ExperienceSummary => Boolean(experience))
  const draftGenerated = question
    ? (generatedQuestions[question.id] ?? Boolean(question.draft))
    : false

  const updateDraft = (value: string) => {
    if (!question) return
    setDrafts((current) => ({ ...current, [question.id]: value }))
  }

  const generateDraft = async () => {
    if (!match || !question || currentExperienceIds.length === 0) return

    setGeneratingQuestionId(question.id)
    setDraftErrors((current) => ({ ...current, [question.id]: '' }))
    try {
      const result = await createCoverLetterDraft({
        matchId: match.id,
        questionId: question.id,
        questionText: question.text,
        experienceIds: currentExperienceIds,
      })
      setDrafts((current) => ({ ...current, [question.id]: result.draft }))
      setGeneratedQuestions((current) => ({ ...current, [question.id]: true }))
    } catch (reason) {
      setDraftErrors((current) => ({
        ...current,
        [question.id]:
          reason instanceof Error ? reason.message : '초안을 작성하지 못했습니다.',
      }))
    } finally {
      setGeneratingQuestionId(null)
    }
  }

  const addExperience = (experienceId: string) => {
    if (!question || !experiences.some((experience) => experience.id === experienceId)) {
      return
    }

    setSelectedExperienceIds((current) => {
      const selected = current[question.id] ?? []
      if (selected.includes(experienceId)) return current
      return { ...current, [question.id]: [...selected, experienceId] }
    })
  }

  const removeExperience = (experienceId: string) => {
    if (!question) return
    setSelectedExperienceIds((current) => ({
      ...current,
      [question.id]: (current[question.id] ?? []).filter(
        (id) => id !== experienceId,
      ),
    }))
  }

  return (
    <section className="matching-column flex min-h-0 flex-col overflow-hidden rounded-[14px] bg-panel max-[760px]:hidden max-[760px]:h-full">
      <div className="border-b border-[#e2e3e7]">
        <PanelHeader title="문항 · 경험 매칭" tone="amber" />
      </div>

      {!match ? (
        <EmptyMatching onStart={onStart} />
      ) : (
        <div className="flex min-h-0 flex-1 flex-col px-3.5">
          <QuestionTabs
            match={match}
            activeQuestion={activeQuestion}
            onQuestionChange={onQuestionChange}
          />
          {question && (
            <>
              <ActiveQuestion text={question.text} />
              <DraftEditor
                selectedExperiences={currentExperiences}
                generated={draftGenerated}
                value={currentDraft}
                loading={generatingQuestionId === question.id}
                error={draftErrors[question.id]}
                onDropExperience={addExperience}
                onRemoveExperience={removeExperience}
                onChange={updateDraft}
                onGenerate={() => void generateDraft()}
              />
            </>
          )}
        </div>
      )}
    </section>
  )
}

function ActiveQuestion({ text }: { text: string }) {
  return <h3 className="mt-2 mb-0 text-[15px] leading-[1.6]">{text}</h3>
}

function EmptyMatching({ onStart }: { onStart: () => void }) {
  return (
    <div className="flex flex-1 flex-col items-center justify-center p-[30px] text-center">
      <span className="flex size-16 items-center justify-center rounded-full bg-white text-brand">
        <Icon name="sparkle" size={28} />
      </span>
      <h3 className="mt-5 mb-[9px] text-xl tracking-[-.4px]">
        문항에 쓸 경험을 찾아보세요.
      </h3>
      <p className="mt-0 mb-[22px] text-[13px] leading-[1.65] text-muted">
        JD와 자기소개서 문항을 입력하면
        <br />내 경험에서 적합한 답변 재료를 추천합니다.
      </p>
      <button
        className="inline-flex items-center justify-center gap-2 rounded-lg bg-brand px-4 py-[11px] text-sm font-bold text-white hover:bg-brand-dark"
        onClick={onStart}
      >
        매칭 시작하기
      </button>
    </div>
  )
}

function QuestionTabs({
  match,
  activeQuestion,
  onQuestionChange,
}: Pick<MatchingCanvasProps, 'match' | 'activeQuestion' | 'onQuestionChange'> & {
  match: MatchResult
}) {
  return (
    <div className="flex gap-2 overflow-x-auto pt-[18px] pb-3.5" role="tablist">
      {match.questions.map((item, index) => (
        <button
          className={`shrink-0 rounded-[7px] px-[13px] py-[9px] text-xs ${
            activeQuestion === index
              ? 'bg-[#dfe4ff] font-bold text-brand'
              : 'bg-[#e8e9ed] text-[#747680]'
          }`}
          role="tab"
          aria-selected={activeQuestion === index}
          key={item.id}
          onClick={() => onQuestionChange(index)}
        >
          {index + 1}번 문항
        </button>
      ))}
    </div>
  )
}
