import { useEffect, useRef, useState } from 'react'
import {
  createMatch,
  getExperience,
  getMatch,
  getResume,
  listExperiences,
  listResumes,
} from '../../api/data-source'
import type {
  ExperienceDetail,
  ExperienceSummary,
  MatchInput,
  MatchResult,
  ResumeDetail,
  ResumeSummary,
} from '../../types'

export type MobileView = 'experiences' | 'matching' | 'resumes'

const initialInput: MatchInput = {
  company: '',
  role: '',
  jobDescription: '',
  questions: [''],
}

const getTimestamp = () => Date.now()

export function useWorkspace(initialMatchingOpen: boolean) {
  const [experiences, setExperiences] = useState<ExperienceSummary[]>([])
  const [resumes, setResumes] = useState<ResumeSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [matchInput, setMatchInput] = useState(initialInput)
  const [match, setMatch] = useState<MatchResult | null>(null)
  const [activeQuestion, setActiveQuestion] = useState(0)
  const [matchModalOpen, setMatchModalOpen] = useState(initialMatchingOpen)
  const [matchStatus, setMatchStatus] = useState('')
  const [matchError, setMatchError] = useState('')
  const [experienceDetail, setExperienceDetail] = useState<ExperienceDetail | null>(null)
  const [experienceLoading, setExperienceLoading] = useState(false)
  const [resumeDetail, setResumeDetail] = useState<ResumeDetail | null>(null)
  const [resumeLoading, setResumeLoading] = useState(false)
  const [mobileView, setMobileView] = useState<MobileView>('matching')
  const [resumeExpanded, setResumeExpanded] = useState(false)
  const pollTimer = useRef<number | null>(null)

  useEffect(() => {
    let active = true

    Promise.all([listExperiences(), listResumes()])
      .then(([experienceData, resumeData]) => {
        if (!active) return
        setExperiences(experienceData)
        setResumes(resumeData)
      })
      .catch((reason: unknown) => {
        if (active) {
          setError(reason instanceof Error ? reason.message : '데이터를 불러오지 못했습니다.')
        }
      })
      .finally(() => {
        if (active) setLoading(false)
      })

    return () => {
      active = false
    }
  }, [])

  useEffect(
    () => () => {
      if (pollTimer.current !== null) window.clearTimeout(pollTimer.current)
    },
    [],
  )

  const stopPolling = () => {
    if (pollTimer.current !== null) window.clearTimeout(pollTimer.current)
    pollTimer.current = null
  }

  const openExperience = async (id: string) => {
    setExperienceDetail(null)
    setExperienceLoading(true)
    try {
      setExperienceDetail(await getExperience(id))
    } finally {
      setExperienceLoading(false)
    }
  }

  const openResume = async (id: string) => {
    setResumeDetail(null)
    setResumeLoading(true)
    try {
      setResumeDetail(await getResume(id))
    } finally {
      setResumeLoading(false)
    }
  }

  const pollMatch = async (id: string, input: MatchInput, startedAt: number): Promise<void> => {
    if (getTimestamp() - startedAt > 120_000) {
      setMatchStatus('timeout')
      setMatchError('분석 대기 시간이 2분을 초과했습니다.')
      return
    }

    const result = await getMatch(id, input)
    if (result.status === 'completed') {
      setMatch(result)
      setMatchStatus('')
      setActiveQuestion(0)
      setMobileView('matching')
      return
    }

    if (result.status === 'failed') {
      setMatchStatus('failed')
      setMatchError(result.error || '추천 결과를 만들지 못했습니다.')
      return
    }

    setMatchStatus(result.status)
    pollTimer.current = window.setTimeout(
      () => void pollMatch(id, input, startedAt),
      2_000,
    )
  }

  const submitMatch = async (input: MatchInput) => {
    stopPolling()
    setMatchInput(input)
    setMatchModalOpen(false)
    setMatchStatus('pending')
    setMatchError('')

    try {
      const created = await createMatch(input)
      await pollMatch(created.id, input, getTimestamp())
    } catch (reason) {
      setMatchStatus('failed')
      setMatchError(reason instanceof Error ? reason.message : '매칭 요청에 실패했습니다.')
    }
  }

  const closeMatchStatus = () => {
    stopPolling()
    setMatchStatus('')
  }

  const retryMatch = () => {
    closeMatchStatus()
    setMatchModalOpen(true)
  }

  return {
    experiences,
    resumes,
    loading,
    error,
    matchInput,
    match,
    activeQuestion,
    matchModalOpen,
    matchStatus,
    matchError,
    experienceDetail,
    experienceLoading,
    resumeDetail,
    resumeLoading,
    mobileView,
    resumeExpanded,
    recommendations: match?.questions[activeQuestion]?.recommendations ?? [],
    setActiveQuestion,
    setMatchModalOpen,
    setExperienceDetail,
    setResumeDetail,
    setMobileView,
    setResumeExpanded,
    openExperience,
    openResume,
    submitMatch,
    closeMatchStatus,
    retryMatch,
  }
}
