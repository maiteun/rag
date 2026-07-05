import type { MatchLevel } from '../../types'

const label = {
  high: '높음',
  medium: '보통',
  low: '낮음',
}

const tone = {
  high: 'bg-[#e9edff] text-brand',
  medium: 'bg-[#fff1d7] text-[#996300]',
  low: 'bg-[#ebecf0] text-[#686a73]',
}

export function MatchLevelChip({ level }: { level: MatchLevel }) {
  return (
    <span className={`shrink-0 rounded-full px-2 py-[5px] text-[10px] font-bold ${tone[level]}`}>
      {label[level]}
    </span>
  )
}
