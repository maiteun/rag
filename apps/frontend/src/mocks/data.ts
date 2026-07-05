import type { ExperienceDetail, MatchInput, MatchResult, ResumeDetail } from '../types'

const projects = [
  ['AI 문서 검색 자동화', '사내 문서 탐색 시간을 줄이기 위해 하이브리드 검색 파이프라인을 구축했습니다.', ['Python', 'FastAPI', 'RAG']],
  ['결제 장애 대응 체계 개선', '반복되는 결제 장애의 원인을 분석하고 관측성과 복구 절차를 개선했습니다.', ['Java', 'Spring', 'Grafana']],
  ['추천 모델 실험 플랫폼', '모델 실험과 지표 비교 과정을 표준화해 반복 실험 시간을 줄였습니다.', ['Python', 'MLflow', 'SQL']],
  ['대규모 로그 파이프라인', '서비스 로그 수집 구조를 재설계하고 처리 지연을 안정화했습니다.', ['Kafka', 'Spark', 'AWS']],
  ['동아리 협업 프로세스 개선', '12명의 팀이 같은 기준으로 일하도록 이슈와 리뷰 절차를 정착시켰습니다.', ['GitHub', 'Notion', 'Leadership']],
  ['고객 문의 분류 모델', '문의 분류 자동화로 담당자 배정 시간을 단축했습니다.', ['PyTorch', 'NLP', 'Docker']],
  ['재고 예측 대시보드', '판매 데이터를 시각화하고 품목별 재고 위험을 조기에 알렸습니다.', ['React', 'TypeScript', 'Chart.js']],
  ['API 응답 속도 개선', '쿼리 병목과 캐시 정책을 개선해 핵심 API 지연을 낮췄습니다.', ['PostgreSQL', 'Redis', 'FastAPI']],
]

export const experiences: ExperienceDetail[] = Array.from({ length: 24 }, (_, index) => {
  const [title, summary, skills] = projects[index % projects.length] as [string, string, string[]]
  const year = 2025 - Math.floor(index / 8)
  return {
    id: `exp_${index + 1}`,
    title: index < projects.length ? title : `${title} ${Math.floor(index / projects.length) + 1}`,
    period: `${year}.${String((index % 6) + 1).padStart(2, '0')} - ${year}.${String((index % 6) + 4).padStart(2, '0')}`,
    summary,
    skills,
    competencies: index % 2 ? ['문제 해결', '협업'] : ['분석', '실행력'],
    organization: index % 3 === 0 ? '교내 AI 프로젝트팀' : '개인·팀 프로젝트',
    role: '요구사항 정의, 핵심 기능 구현 및 결과 검증',
    situation: '기존 과정이 수작업에 의존해 처리 시간이 길고 결과 편차가 컸습니다.',
    task: '제한된 일정 안에 반복 가능한 해결 방식을 설계하고 팀이 사용할 수 있게 만드는 것이 목표였습니다.',
    action: '사용 흐름과 병목을 측정하고 작은 단위의 실험을 반복했습니다. API와 데이터 모델을 정리하고 리뷰를 통해 품질을 검증했습니다.',
    result: index % 2 ? '처리 시간을 약 40% 줄이고 운영 절차를 문서화했습니다.' : '핵심 지표를 개선하고 후속 팀이 재사용할 수 있는 구조를 남겼습니다.',
    learned: '기술 선택보다 문제와 성공 기준을 먼저 합의하는 것이 중요하다는 점을 배웠습니다.',
    evidence: [{ sourceId: `resume_${(index % 6) + 1}`, label: `${year} 개발자 이력서`, excerpt: '프로젝트 경험 및 정량 성과 기술' }],
  }
})

export const resumes: ResumeDetail[] = Array.from({ length: 12 }, (_, index) => ({
  id: `resume_${index + 1}`,
  title: `${2026 - Math.floor(index / 3)} ${['AI 엔지니어', '백엔드', '데이터'][index % 3]} 이력서`,
  fileName: `resume_${2026 - Math.floor(index / 3)}_${index + 1}.pdf`,
  createdAt: new Date(2026 - Math.floor(index / 3), (8 - index + 12) % 12, 12).toISOString(),
  experienceCount: 3 + (index % 4),
  status: 'processed',
  signal: index < 2 ? (index === 0 ? '최근 업데이트' : '면접 활용') : undefined,
  rawText: `지원 직무에 필요한 문제 해결 역량과 협업 경험을 중심으로 작성한 이력서입니다.\n\n주요 경험\n- 서비스의 병목을 정의하고 데이터로 검증\n- 팀과 함께 설계부터 배포까지 수행\n- 결과와 회고를 문서화하여 재사용 가능한 지식으로 정리`,
  experienceIds: [`exp_${(index % 8) + 1}`, `exp_${((index + 2) % 8) + 1}`, `exp_${((index + 4) % 8) + 1}`],
}))

const reasons = [
  '문제 상황과 해결 과정, 본인의 기술적 기여가 구체적으로 드러납니다.',
  '협업 과정에서 맡은 역할과 팀에 만든 변화가 문항 의도와 맞습니다.',
  '직무에 필요한 기술을 실제 결과로 연결한 근거가 충분합니다.',
  '제약 조건 아래 우선순위를 정하고 실행한 과정이 명확합니다.',
]

export function createMockMatch(input: MatchInput, id = `match_${Date.now()}`): MatchResult {
  return {
    id,
    status: 'completed',
    company: input.company,
    role: input.role,
    jobDescription: input.jobDescription,
    jobAnalysis: {
      summary: `${input.role || '지원 직무'}에서 문제를 구조화하고 구현 결과를 만드는 역량을 요구합니다.`,
      requiredSkills: ['문제 해결', '데이터 기반 의사결정', '협업'],
      competencies: ['주도성', '실행력', '커뮤니케이션'],
    },
    questions: input.questions.map((text, questionIndex) => ({
      id: `q_${questionIndex + 1}`,
      text,
      intent: questionIndex % 2 ? '협업 상황에서 맡은 역할과 기여 방식을 확인합니다.' : '문제를 정의하고 해결한 과정과 결과를 확인합니다.',
      requiredElements: questionIndex % 2 ? ['협업 배경', '본인 역할', '의견 조율', '결과'] : ['문제 상황', '본인 역할', '해결 과정', '결과'],
      recommendations: Array.from({ length: 4 }, (_, rankIndex) => ({
        experienceId: `exp_${((questionIndex * 4 + rankIndex) % 12) + 1}`,
        rank: rankIndex + 1,
        score: 0.91 - rankIndex * 0.12,
        matchLevel: rankIndex < 2 ? 'high' as const : rankIndex === 2 ? 'medium' as const : 'low' as const,
        reason: reasons[(questionIndex + rankIndex) % reasons.length],
      })),
    })),
  }
}
