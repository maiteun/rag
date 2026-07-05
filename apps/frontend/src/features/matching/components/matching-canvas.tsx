import { Icon } from '../../../components/ui/icon'
import { PanelHeader, PanelMessage } from '../../../components/ui/panel'
import { MatchLevelChip } from '../../../components/ui/match-level-chip'
import type { MatchResult, Recommendation } from '../../../types'

interface MatchingCanvasProps {
  match: MatchResult | null
  activeQuestion: number
  onQuestionChange: (index: number) => void
  onStart: () => void
  onExperience: (id: string) => void
}

export function MatchingCanvas({
  match,
  activeQuestion,
  onQuestionChange,
  onStart,
  onExperience,
}: MatchingCanvasProps) {
  const question = match?.questions[activeQuestion]

  return (
    <section className="matching-column flex min-h-0 flex-col overflow-hidden rounded-[14px] bg-panel max-[760px]:hidden max-[760px]:h-full">
      <div className="border-b border-[#e2e3e7]">
        <PanelHeader title="문항 · 경험 매칭" tone="amber" />
      </div>

      {!match ? (
        <EmptyMatching onStart={onStart} />
      ) : (
        <div className="min-h-0 overflow-auto px-3.5 pb-4 [overscroll-behavior:contain] [scrollbar-width:thin]">
          <QuestionTabs
            match={match}
            activeQuestion={activeQuestion}
            onQuestionChange={onQuestionChange}
          />
          {question && (
            <>
              {/* <QuestionCard question={question} number={activeQuestion + 1} /> */}
              <RecommendationList
                recommendations={question.recommendations}
                onExperience={onExperience}
              />
            </>
          )}
        </div>
      )}
    </section>
  )
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

function RecommendationList({
  recommendations,
  onExperience,
}: {
  recommendations: Recommendation[]
  onExperience: (id: string) => void
}) {
  return (
    <section className="mt-5">
      <header className="mx-0.5 mb-2.5 flex items-end justify-between">
        <div className="flex items-center gap-[7px]">
          <h3 className="m-0 text-[15px]">추천 경험</h3>
        </div>
        <p className="m-0 text-[12px] text-[#898b94]">
          관련성과 근거의 명확성을 기준으로 정렬했습니다.
        </p>
      </header>

      {recommendations.length ? (
        recommendations.map((recommendation) => (
          <RecommendationCard
            key={recommendation.experienceId}
            recommendation={recommendation}
            onExperience={onExperience}
          />
        ))
      ) : (
        <PanelMessage>현재 기록에서는 충분히 적합한 경험을 찾지 못했습니다.</PanelMessage>
      )}
    </section>
  )
}

function RecommendationCard({
  recommendation,
  onExperience,
}: {
  recommendation: Recommendation
  onExperience: (id: string) => void
}) {
  return (
    <button
      className="mb-[9px] grid w-full grid-cols-[auto_1fr_auto_auto] items-center gap-3 rounded-[10px] border border-[#e5e6e9] bg-white p-3.5 text-left hover:border-[#b8c3ef]"
      onClick={() => onExperience(recommendation.experienceId)}
    >
      <span className="text-lg font-black text-brand">
        {String(recommendation.rank).padStart(2, '0')}
      </span>
      <span>
        <strong className="block text-xs leading-normal">{recommendation.reason}</strong>
        <small className="mt-[5px] block text-[12px] text-[#92949d]">
          경험 상세에서 역할과 성과 근거를 확인할 수 있습니다.
        </small>
      </span>
      <MatchLevelChip level={recommendation.matchLevel} />
    </button>
  )
}
