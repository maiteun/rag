import { useState } from 'react'
import { Icon } from '../../../components/ui/icon'
import { Modal } from '../../../components/ui/modal'
import type { MatchInput } from '../../../types'

interface MatchCreateModalProps {
  initialValue: MatchInput
  onClose: () => void
  onSubmit: (input: MatchInput) => Promise<void>
}

const fieldClass =
  'w-full resize-none rounded-lg border border-[#d8d9de] p-3 text-[13px] outline-0 focus:border-brand focus:shadow-[0_0_0_3px_rgba(23,70,245,.08)]'

export function MatchCreateModal({
  initialValue,
  onClose,
  onSubmit,
}: MatchCreateModalProps) {
  const [value, setValue] = useState(initialValue)
  const [tab, setTab] = useState<'jd' | 'questions'>('jd')
  const [submitted, setSubmitted] = useState(false)
  const [busy, setBusy] = useState(false)

  const valid = Boolean(
    value.jobDescription.trim() &&
      value.questions.length &&
      value.questions.every((question) => question.trim()),
  )

  const submit = async () => {
    setSubmitted(true)
    if (!valid || busy) return

    setBusy(true)
    await onSubmit({
      ...value,
      questions: value.questions.map((question) => question.trim()),
    }).finally(() => setBusy(false))
  }

  return (
    <Modal
      title="지원 정보를 입력하면 문항별 경험을 추천해 드려요."
      size="form"
      onClose={onClose}
      footer={
        <MatchFormFooter valid={valid} busy={busy} onSubmit={submit} />
      }
    >
      <div className="h-full p-6">
        <CompanyFields value={value} onChange={setValue} />
        <FormTabs
          tab={tab}
          questionCount={value.questions.length}
          onChange={setTab}
        />
        <div className="pt-5">
          {tab === 'jd' ? (
            <JobDescriptionField
              value={value}
              submitted={submitted}
              onChange={setValue}
            />
          ) : (
            <QuestionFields
              value={value}
              submitted={submitted}
              onChange={setValue}
            />
          )}
        </div>
      </div>
    </Modal>
  )
}

function MatchFormFooter({
  valid,
  busy,
  onSubmit,
}: {
  valid: boolean
  busy: boolean
  onSubmit: () => void
}) {
  return (
    <>
      <span className="text-xs text-muted max-[760px]:hidden">
        JD와 문항을 모두 입력해야 합니다.
      </span>
      <button
        className="inline-flex items-center justify-center gap-2 rounded-lg bg-brand px-6 py-[11px] text-sm font-bold text-white hover:bg-brand-dark disabled:cursor-not-allowed disabled:bg-[#abb2c8]"
        disabled={!valid || busy}
        onClick={onSubmit}
      >
        {busy ? '요청 중…' : '매칭하기 !'}
        {/* <Icon name="arrow" size={18} /> */}
      </button>
    </>
  )
}

function CompanyFields({
  value,
  onChange,
}: {
  value: MatchInput
  onChange: (value: MatchInput) => void
}) {
  return (
    <div className="grid grid-cols-2 gap-3.5 max-[760px]:grid-cols-1">
      <FormField label="회사명" optional>
        <input
          className={fieldClass}
          value={value.company}
          onChange={(event) => onChange({ ...value, company: event.target.value })}
          placeholder="예: 모람 테크"
        />
      </FormField>
      <FormField label="직무명" optional>
        <input
          className={fieldClass}
          value={value.role}
          onChange={(event) => onChange({ ...value, role: event.target.value })}
          placeholder="예: 백엔드 엔지니어"
        />
      </FormField>
    </div>
  )
}

function FormField({
  label,
  optional = false,
  children,
}: {
  label: string
  optional?: boolean
  children: React.ReactNode
}) {
  return (
    <label>
      <span className="mb-2 block text-xs font-bold">
        {label} {optional && <em className="font-medium not-italic text-[#a0a1a9]">선택</em>}
      </span>
      {children}
    </label>
  )
}

function FormTabs({
  tab,
  questionCount,
  onChange,
}: {
  tab: 'jd' | 'questions'
  questionCount: number
  onChange: (tab: 'jd' | 'questions') => void
}) {
  return (
    <div className="mt-6 flex gap-[22px] border-b border-line" role="tablist">
      <FormTab active={tab === 'jd'} onClick={() => onChange('jd')}>
        채용 공고
      </FormTab>
      <FormTab active={tab === 'questions'} onClick={() => onChange('questions')}>
        자기소개서 문항
        <span className="ml-1 rounded-full bg-[#e8e9ed] px-1.5 py-0.5 text-[10px]">
          {questionCount}
        </span>
      </FormTab>
    </div>
  )
}

function FormTab({
  active,
  children,
  onClick,
}: {
  active: boolean
  children: React.ReactNode
  onClick: () => void
}) {
  return (
    <button
      className={`bg-transparent px-0.5 pb-3 text-[13px] ${
        active
          ? 'border-b-2 border-brand font-bold text-brand'
          : 'text-[#7d7f89]'
      }`}
      role="tab"
      aria-selected={active}
      onClick={onClick}
    >
      {children}
    </button>
  )
}

function JobDescriptionField({
  value,
  submitted,
  onChange,
}: {
  value: MatchInput
  submitted: boolean
  onChange: (value: MatchInput) => void
}) {
  return (
    <FormField label="JD 원문">
      <textarea
        autoFocus
        className={`${fieldClass} h-[245px]`}
        value={value.jobDescription}
        onChange={(event) => onChange({ ...value, jobDescription: event.target.value })}
        placeholder="주요 업무, 자격 요건, 우대 사항을 붙여 넣어 주세요."
      />
      {submitted && !value.jobDescription.trim() && (
        <FormError>JD를 입력해 주세요.</FormError>
      )}
    </FormField>
  )
}

function QuestionFields({
  value,
  submitted,
  onChange,
}: {
  value: MatchInput
  submitted: boolean
  onChange: (value: MatchInput) => void
}) {
  const updateQuestion = (index: number, question: string) => {
    const questions = [...value.questions]
    questions[index] = question
    onChange({ ...value, questions })
  }

  const removeQuestion = (index: number) => {
    onChange({
      ...value,
      questions: value.questions.filter((_, itemIndex) => itemIndex !== index),
    })
  }

  return (
    <div className="grid gap-4">
      {value.questions.map((question, index) => (
        <FormField label={`문항 ${index + 1}`} key={index}>
          <div className="flex items-start gap-[7px]">
            <textarea
              className={`${fieldClass} h-[88px]`}
              value={question}
              onChange={(event) => updateQuestion(index, event.target.value)}
              placeholder="자기소개서 문항을 입력해 주세요."
            />
            {value.questions.length > 1 && (
              <button
                className="mt-[3px] inline-flex items-center justify-center rounded-[7px] bg-transparent p-[7px] text-[#666976] hover:bg-[#f0f0f2]"
                aria-label={`${index + 1}번 문항 삭제`}
                onClick={() => removeQuestion(index)}
              >
                <Icon name="trash" size={18} />
              </button>
            )}
          </div>
          {submitted && !question.trim() && (
            <FormError>빈 문항은 제출할 수 없습니다.</FormError>
          )}
        </FormField>
      ))}
      <button
        className="flex items-center justify-center gap-[7px] rounded-lg border border-dashed border-[#b8bac2] bg-white p-[11px] text-xs text-[#5f616c]"
        onClick={() => onChange({ ...value, questions: [...value.questions, ''] })}
      >
        <Icon name="plus" size={18} /> 문항 추가
      </button>
    </div>
  )
}

function FormError({ children }: { children: React.ReactNode }) {
  return <small className="mt-1.5 block text-[11px] text-[#cf3434]">{children}</small>
}
