import { Modal } from '../../../components/ui/modal'
import { TagList } from '../../../components/ui/tag-list'
import { DetailSkeleton } from '../../../components/ui/detail-skeleton'
import type { ExperienceDetail } from '../../../types'

interface ExperienceDetailModalProps {
  data: ExperienceDetail | null
  loading: boolean
  onClose: () => void
  onResume: (id: string) => void
}

export function ExperienceDetailModal({
  data,
  loading,
  onClose,
  onResume,
}: ExperienceDetailModalProps) {
  return (
    <Modal
      title="경험 상세"
      size="detail"
      onClose={onClose}
    >
      {loading || !data ? (
        <DetailSkeleton />
      ) : (
        <ExperienceDetailContent data={data} onResume={onResume} />
      )}
    </Modal>
  )
}

function ExperienceDetailContent({
  data,
  // onResume,
}: {
  data: ExperienceDetail
  onResume: (id: string) => void
}) {
  const sections: Array<[string, string | undefined]> = [
    ['역할', data.role],
    ['문제 상황', data.situation],
    ['수행 과제', data.task],
    ['수행 행동', data.action],
    ['결과 및 성과', data.result],
    ['배운 점', data.learned],
  ]

  return (
    <div className="p-[26px]">
      <header className="flex items-start justify-between gap-5">
        <div>
          <h3 className="mb-1 text-[25px] tracking-[-.7px]">{data.title}</h3>
          <p className="m-0 text-sm text-muted">
            {[data.organization, data.period].filter(Boolean).join(' · ')}
          </p>
        </div>
        <TagList
          className="max-w-[42%] justify-end"
          items={[...data.skills, ...data.competencies]}
          tone="blue"
        />
      </header>

      <p className="mt-[25px] mb-0 pb-[23px] text-[15px] leading-[1.7]">
        {data.summary}
      </p>

      <div className="mt-2 grid grid-cols-2 gap-4 max-[760px]:grid-cols-1">
        {sections.map(([title, content]) => {
          if (!content) return null

          return (
            <DetailSection
              key={title}
              title={title}
              content={content}
            />
          )
        })}
      </div>

      {/* <EvidenceList data={data} onResume={onResume} /> */}
    </div>
  )
}

function DetailSection({
  title,
  content,
}: {
  title: string
  content: string
}) {
  return (
    <section className="min-h-[126px] rounded-xl border border-[#e8e9ed] bg-[#f7f7f8] p-5 max-[760px]:min-h-0">
      <h4 className="mt-0 mb-1 text-sm text-muted">{title}</h4>
      <p className="m-0 text-sm leading-[1.65]">{content}</p>
    </section>
  )
}

// function EvidenceList({
//   data,
//   onResume,
// }: {
//   data: ExperienceDetail
//   onResume: (id: string) => void
// }) {
//   return (
//     <section className="pt-[23px]">
//       <h4 className="mt-0 mb-2.5 text-xs text-brand">근거 자료</h4>
//       {data.evidence.length ? (
//         data.evidence.map((item) => (
//           <button
//             className="mt-2 grid w-full grid-cols-[auto_1fr_auto] items-center gap-3 rounded-[9px] bg-[#f6f6f8] p-3 text-left"
//             key={item.sourceId}
//             onClick={() => onResume(item.sourceId)}
//           >
//             <span className="flex size-9 items-center justify-center rounded-[7px] bg-brand-soft text-brand">
//               <Icon name="file" />
//             </span>
//             <span>
//               <strong className="block text-xs">{item.label}</strong>
//               <small className="mt-1 block text-[12px] text-muted">{item.excerpt}</small>
//             </span>
//             <Icon name="arrow" />
//           </button>
//         ))
//       ) : (
//         <p className="text-xs text-muted">연결된 근거 자료가 없습니다.</p>
//       )}
//     </section>
//   )
// }
