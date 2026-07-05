import { Modal } from '../../../components/ui/modal'

interface MatchStatusModalProps {
  status: string
  error: string
  onClose: () => void
  onRetry: () => void
}

export function MatchStatusModal({
  status,
  error,
  onClose,
  onRetry,
}: MatchStatusModalProps) {
  const failed = status === 'failed' || status === 'timeout'

  return (
    <Modal
      title="문항과 경험 매칭"
      subtitle="입력한 내용을 바탕으로 경험을 분석합니다."
      size="form"
      onClose={onClose}
      footer={failed ? <RetryFooter onRetry={onRetry} /> : undefined}
    >
      <div className="flex h-full flex-col items-center justify-center p-10 text-center">
        {failed ? <FailureState error={error} /> : <LoadingState />}
      </div>
    </Modal>
  )
}

function RetryFooter({ onRetry }: { onRetry: () => void }) {
  return (
    <>
      <span />
      <button
        className="rounded-lg bg-brand px-4 py-[11px] text-sm font-bold text-white hover:bg-brand-dark"
        onClick={onRetry}
      >
        다시 시도
      </button>
    </>
  )
}

function FailureState({ error }: { error: string }) {
  return (
    <>
      <span className="flex size-[62px] items-center justify-center rounded-full bg-[#fff0f0] text-[25px] font-extrabold text-[#c42c2c]">
        !
      </span>
      <StateMessage
        title="분석을 완료하지 못했습니다."
        body={error || '잠시 후 다시 시도해 주세요.'}
      />
    </>
  )
}

function LoadingState() {
  return (
    <>
      <div className="flex gap-[7px]">
        {[0, 150, 300].map((delay) => (
          <span
            className="size-2.5 animate-[loader_1s_infinite_alternate] rounded-full bg-brand"
            style={{ animationDelay: `${delay}ms` }}
            key={delay}
          />
        ))}
      </div>
      <StateMessage
        title="경험을 분석하고 있어요."
        body={
          <>
            문항과 관련 있는 경험을 찾고
            <br />추천 근거를 정리하고 있습니다.
          </>
        }
      />
    </>
  )
}

function StateMessage({
  title,
  body,
}: {
  title: string
  body: React.ReactNode
}) {
  return (
    <>
      <h3 className="mt-[25px] mb-[9px] text-[21px]">{title}</h3>
      <p className="m-0 text-sm leading-[1.6] text-muted">{body}</p>
    </>
  )
}
