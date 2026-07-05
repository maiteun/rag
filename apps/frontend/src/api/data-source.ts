import { createMockMatch, experiences, resumes } from '../mocks/data'
import type {
  CoverLetterDraft,
  DataMode,
  DraftInput,
  ExperienceDetail,
  ExperienceSummary,
  MatchInput,
  MatchLevel,
  MatchResult,
  ResumeDetail,
  ResumeSummary,
} from '../types'

const mode = (import.meta.env.VITE_DATA_MODE || 'mock') as DataMode
const baseUrl = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api').replace(/\/$/, '')
const userId = import.meta.env.VITE_USER_ID || '00000000-0000-0000-0000-000000000001'

interface Envelope<T> { success: boolean; message: string; data?: T }

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, { ...init, headers: { 'Content-Type': 'application/json', ...init?.headers } })
  const body = await response.json() as Envelope<T>
  if (!response.ok || !body.success || !body.data) throw new Error(body.message || '요청을 처리하지 못했습니다.')
  return body.data
}

function period(start?: string, end?: string) {
  if (!start && !end) return undefined
  return `${start?.slice(0, 7).replace('-', '.') || ''} - ${end?.slice(0, 7).replace('-', '.') || '현재'}`
}

function level(score?: number): MatchLevel {
  if ((score || 0) >= .8) return 'high'
  if ((score || 0) >= .6) return 'medium'
  return 'low'
}

async function apiOrMock<T>(apiCall: () => Promise<T>, mockValue: () => T): Promise<T> {
  if (mode === 'mock') return mockValue()
  try { return await apiCall() } catch (error) {
    if (mode === 'hybrid') return mockValue()
    throw error
  }
}

export async function listExperiences(): Promise<ExperienceSummary[]> {
  return apiOrMock(async () => {
    const data = await request<{ experiences: Array<Record<string, unknown>> }>(`/experiences?user_id=${encodeURIComponent(userId)}`)
    return data.experiences.map(item => ({ id: String(item.id), title: String(item.title), summary: String(item.summary || ''), skills: item.skills as string[] || [], competencies: item.competencies as string[] || [] }))
  }, () => experiences)
}

export async function getExperience(id: string): Promise<ExperienceDetail> {
  return apiOrMock(async () => {
    const item = await request<Record<string, unknown>>(`/experiences/${id}`)
    return {
      id: String(item.id), title: String(item.title), summary: String(item.summary || ''), skills: item.skills as string[] || [],
      competencies: item.competencies as string[] || [], period: period(item.start_date as string, item.end_date as string),
      organization: item.organization as string, role: item.role as string, situation: item.situation as string,
      task: item.task as string, action: item.action as string, result: item.result as string, learned: item.learned as string,
      evidence: ((item.sources || []) as Array<Record<string, unknown>>).map(source => ({ sourceId: String(source.source_document_id), label: String(source.title || '출처 문서'), excerpt: source.excerpt as string })),
    }
  }, () => experiences.find(item => item.id === id) || experiences[0])
}

export async function listResumes(): Promise<ResumeSummary[]> {
  return apiOrMock<ResumeSummary[]>(async () => {
    const data = await request<{ resumes: Array<Record<string, unknown>> }>(`/resumes?user_id=${encodeURIComponent(userId)}`)
    return data.resumes.map(item => ({ id: String(item.id), title: String(item.title || item.original_filename || '제목 없는 이력서'), fileName: item.original_filename as string, createdAt: String(item.created_at), status: item.status as string }))
  }, () => resumes)
}

export async function getResume(id: string): Promise<ResumeDetail> {
  return apiOrMock<ResumeDetail>(async () => {
    const item = await request<Record<string, unknown>>(`/resumes/${id}`)
    return { id: String(item.id), title: String(item.title || item.original_filename || '제목 없는 이력서'), fileName: item.original_filename as string, createdAt: String(item.created_at), status: item.status as string, rawText: String(item.raw_text || ''), experienceIds: [] }
  }, () => resumes.find(item => item.id === id) || resumes[0])
}

export async function createMatch(input: MatchInput): Promise<{ id: string; status: string }> {
  if (mode === 'mock') return new Promise(resolve => setTimeout(() => resolve({ id: `match_${Date.now()}`, status: 'pending' }), 650))
  try {
    const data = await request<{ match_id: string; status: string }>('/matches', { method: 'POST', body: JSON.stringify({ user_id: userId, job_description: input.jobDescription, questions: input.questions }) })
    return { id: data.match_id, status: data.status }
  } catch (error) {
    if (mode === 'hybrid') return { id: `match_${Date.now()}`, status: 'pending' }
    throw error
  }
}

export async function getMatch(id: string, input: MatchInput): Promise<MatchResult> {
  if (mode === 'mock' || (mode === 'hybrid' && id.startsWith('match_'))) return createMockMatch(input, id)
  const item = await request<Record<string, unknown>>(`/matches/${id}`)
  const questions = (item.questions || []) as Array<Record<string, unknown>>
  return {
    id: String(item.id), status: String(item.status) as MatchResult['status'], jobDescription: String(item.job_description || input.jobDescription),
    company: input.company, role: input.role,
    questions: questions.map(question => ({
      id: String(question.id), text: String(question.text), draft: question.draft as string | undefined, requiredElements: [],
      recommendations: ((question.recommendations || []) as Array<Record<string, unknown>>).map(rec => ({ experienceId: String(rec.experience_id), rank: Number(rec.rank), score: Number(rec.score), matchLevel: level(Number(rec.score)), reason: String(rec.reason || '직무 및 문항과 관련성이 높은 경험입니다.') })),
    })),
  }
}

export async function createCoverLetterDraft(input: DraftInput): Promise<CoverLetterDraft> {
  return apiOrMock(
    async () => {
      const data = await request<{
        draft: string
        used_experience_ids?: string[]
      }>('/cover-letters/drafts', {
        method: 'POST',
        body: JSON.stringify({
          user_id: userId,
          match_id: input.matchId,
          question_id: input.questionId,
          question_text: input.questionText,
          selected_experience_ids: input.experienceIds,
        }),
      })

      return {
        draft: data.draft,
        usedExperienceIds: data.used_experience_ids ?? input.experienceIds,
      }
    },
    () => createMockDraft(input),
  )
}

function createMockDraft(input: DraftInput): CoverLetterDraft {
  const selectedExperiences = input.experienceIds.flatMap((id) => {
    const experience = experiences.find((item) => item.id === id)
    return experience ? [experience] : []
  })
  const evidence = selectedExperiences
    .map((experience) => `${experience.title}: ${experience.summary}`)
    .join(' ')

  return {
    draft: evidence
      ? `${input.questionText}\n\n${evidence}`
      : `${input.questionText}\n\n선택된 경험을 바탕으로 작성할 초안입니다.`,
    usedExperienceIds: input.experienceIds,
  }
}
