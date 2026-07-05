export function DetailSkeleton() {
  return (
    <div className="grid gap-[11px] p-[30px]">
      {[65, 100, 65, 65].map((width, index) => (
        <span
          className="mb-[25px] block h-[18px] animate-[shimmer_1s_infinite_alternate] rounded bg-[#dedfe3]"
          style={{ width: `${width}%` }}
          key={index}
        />
      ))}
    </div>
  )
}
