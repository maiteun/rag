import type { ReactNode } from 'react'

export function PanelHeader({
  title,
  count,
  action,
}: {
  title: string
  count?: number
  tone?: 'blue' | 'amber' | 'sky'
  action?: ReactNode
}) {
  return (
    <header className="flex min-h-16 shrink-0 items-center justify-between px-[18px]">
      <div className="flex items-center gap-2">
        <h2 className="m-0 text-base font-bold">{title}</h2>
        {count !== undefined && (
          <span className="inline-flex h-5 min-w-5 items-center justify-center rounded-full bg-[#e6e7eb] text-[10px] text-[#757782]">
            {count}
          </span>
        )}
      </div>
      {action}
    </header>
  )
}

export function PanelMessage({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-[150px] flex-col items-center justify-center p-6 text-center text-xs leading-6 text-[#94969f]">
      {children}
    </div>
  )
}

export function PanelSkeleton() {
  return (
    <div className="grid gap-[11px]">
      {[1, 2, 3].map((item) => (
        <div className="rounded-[10px] bg-white p-[18px]" key={item}>
          <span className="mb-3 block h-2.5 w-2/3 animate-[shimmer_1s_infinite_alternate] rounded bg-[#dedfe3]" />
          <span className="mb-3 block h-2.5 w-full animate-[shimmer_1s_infinite_alternate] rounded bg-[#dedfe3]" />
          <span className="block h-2.5 w-2/5 animate-[shimmer_1s_infinite_alternate] rounded bg-[#dedfe3]" />
        </div>
      ))}
    </div>
  )
}
