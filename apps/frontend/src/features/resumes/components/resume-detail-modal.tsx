import { Icon } from '../../../components/ui/icon'
import { Modal } from '../../../components/ui/modal'
import { DetailSkeleton } from '../../../components/ui/detail-skeleton'
import type { ExperienceSummary, ResumeDetail } from '../../../types'

interface ResumeDetailModalProps {
  data: ResumeDetail | null
  loading: boolean
  experiences: ExperienceSummary[]
  onClose: () => void
  onExperience: (id: string) => void
}

export function ResumeDetailModal({
  data,
  loading,
  experiences,
  onClose,
  onExperience,
}: ResumeDetailModalProps) {
  return (
    <Modal
      title="과거 이력서"
      subtitle="원문과 이력서에서 추출한 경험을 함께 확인하세요."
      size="resume"
      onClose={onClose}
    >
      {loading || !data ? (
        <DetailSkeleton />
      ) : (
        <ResumeDetailContent
          data={data}
          experiences={experiences}
          onExperience={onExperience}
        />
      )}
    </Modal>
  )
}

function ResumeDetailContent({
  data,
  experiences,
  onExperience,
}: Pick<ResumeDetailModalProps, 'experiences' | 'onExperience'> & { data: ResumeDetail }) {
  return (
    <div className="p-[26px]">
      <header className="flex items-start justify-between gap-5">
        <div>
          <span className="text-[10px] font-black tracking-[.8px] text-brand">RESUME</span>
          <h3 className="my-[7px] text-[25px] tracking-[-.7px]">{data.title}</h3>
          <p className="m-0 text-xs text-muted">
            {data.fileName} · {new Date(data.createdAt).toLocaleDateString('ko-KR')}
          </p>
        </div>
        {data.fileUrl && (
          <a
            className="inline-flex items-center justify-center rounded-lg border border-[#d8d9df] bg-white px-4 py-[11px] text-sm font-bold text-ink no-underline hover:bg-[#f7f7f8]"
            href={data.fileUrl}
            target="_blank"
            rel="noreferrer"
          >
            새 탭에서 열기
          </a>
        )}
      </header>

      <div className="mt-6 grid grid-cols-[1.45fr_.75fr] gap-[22px] max-[760px]:grid-cols-1">
        <DocumentPreview text={data.rawText} />
        <LinkedExperiences
          ids={data.experienceIds}
          experiences={experiences}
          onExperience={onExperience}
        />
      </div>
    </div>
  )
}

function DocumentPreview({ text }: { text: string }) {
  return (
    <section className="overflow-hidden rounded-[10px] border border-line">
      <header className="border-b border-line bg-[#f5f5f7] px-[15px] py-3 text-xs font-bold">
        추출 텍스트
      </header>
      <article className="min-h-[400px] whitespace-pre-wrap p-[18px] text-[13px] leading-[1.8] text-[#444650]">
        {text || '추출된 텍스트가 없습니다.'}
      </article>
    </section>
  )
}

function LinkedExperiences({
  ids,
  experiences,
  onExperience,
}: {
  ids: string[]
  experiences: ExperienceSummary[]
  onExperience: (id: string) => void
}) {
  const linked = ids
    .map((id) => experiences.find((experience) => experience.id === id))
    .filter((item): item is ExperienceSummary => Boolean(item))

  return (
    <section>
      <h4 className="mt-0 mb-2.5 text-sm text-ink">추출된 경험</h4>
      {linked.length ? (
        linked.map((item) => (
          <button
            className="mb-[9px] grid w-full grid-cols-[1fr_auto] items-center gap-[9px] rounded-[9px] bg-[#f6f6f8] p-[13px] text-left"
            key={item.id}
            onClick={() => onExperience(item.id)}
          >
            <span>
              <strong className="block text-xs">{item.title}</strong>
              <small className="mt-[5px] line-clamp-2 text-[10px] leading-[1.45] text-muted">
                {item.summary}
              </small>
            </span>
            <Icon name="arrow" />
          </button>
        ))
      ) : (
        <p className="text-xs text-muted">연결 경험 정보가 없습니다.</p>
      )}
    </section>
  )
}
