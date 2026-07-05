export type DataMode = 'mock' | 'api' | 'hybrid'
export type MatchStatus = 'pending' | 'queued' | 'processing' | 'completed' | 'failed'
export type MatchLevel = 'high' | 'medium' | 'low'

export interface ExperienceSummary {
  id: string
  title: string
  period?: string
  summary: string
  skills: string[]
  competencies?: string[]
}

export interface Evidence {
  sourceId: string
  label: string
  excerpt?: string
}

export interface ExperienceDetail extends ExperienceSummary {
  organization?: string
  role?: string
  situation?: string
  task?: string
  action?: string
  result?: string
  learned?: string
  competencies: string[]
  evidence: Evidence[]
}

export interface ResumeSummary {
  id: string
  title: string
  fileName?: string
  createdAt: string
  experienceCount?: number
  status?: string
  signal?: string
}

export interface ResumeDetail extends ResumeSummary {
  rawText: string
  fileUrl?: string
  experienceIds: string[]
}

export interface Recommendation {
  experienceId: string
  rank: number
  score?: number
  matchLevel: MatchLevel
  reason: string
}

export interface MatchQuestion {
  id: string
  text: string
  draft?: string
  intent?: string
  requiredElements: string[]
  recommendations: Recommendation[]
}

export interface DraftInput {
  matchId: string
  questionId: string
  questionText: string
  experienceIds: string[]
}

export interface CoverLetterDraft {
  draft: string
  usedExperienceIds: string[]
}

export interface MatchResult {
  id: string
  status: MatchStatus
  company?: string
  role?: string
  jobDescription: string
  jobAnalysis?: {
    summary: string
    requiredSkills: string[]
    competencies: string[]
  }
  questions: MatchQuestion[]
  error?: string
}

export interface MatchInput {
  company?: string
  role?: string
  jobDescription: string
  questions: string[]
}
