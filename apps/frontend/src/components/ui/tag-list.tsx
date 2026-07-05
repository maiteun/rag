interface TagListProps {
  items: string[]
  tone?: 'gray' | 'blue'
  className?: string
}

const toneClass = {
  gray: 'bg-[#f0f1f3] text-[#676975]',
  blue: 'bg-brand-soft text-brand-dark',
}

export function TagList({ items, tone = 'gray', className = '' }: TagListProps) {
  return (
    <div className={`flex flex-wrap gap-[5px] ${className}`}>
      {items.map((item) => (
        <span
          className={`rounded-[5px] px-[7px] py-[5px] text-[11px] ${toneClass[tone]}`}
          key={item}
        >
          {item}
        </span>
      ))}
    </div>
  )
}
