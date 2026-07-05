import type { ReactNode } from 'react'

const paths: Record<string, ReactNode> = {
  archive: (
    <>
      <rect x="4" y="5" width="16" height="15" rx="2" />
      <path d="M8 5V3h8v2M8 10h8M9 14h6" />
    </>
  ),
  arrow: (
    <>
      <path d="M5 12h14M14 7l5 5-5 5" />
    </>
  ),
  briefcase: (
    <>
      <rect x="3" y="7" width="18" height="13" rx="2" />
      <path d="M9 7V4h6v3M3 12h18" />
    </>
  ),
  chevron: <path d="m8 10 4 4 4-4" />,
  close: <path d="M5 5l14 14M19 5 5 19" />,
  file: (
    <>
      <path d="M6 3h8l4 4v14H6zM14 3v5h5M9 13h6M9 17h5" />
    </>
  ),
  grid: (
    <>
      <rect x="4" y="4" width="6" height="6" rx="1" />
      <rect x="14" y="4" width="6" height="6" rx="1" />
      <rect x="4" y="14" width="6" height="6" rx="1" />
      <rect x="14" y="14" width="6" height="6" rx="1" />
    </>
  ),
  home: (
    <>
      <path d="m4 11 8-7 8 7v9H4z" />
      <path d="M9 20v-6h6v6" />
    </>
  ),
  plus: <path d="M12 5v14M5 12h14" />,
  search: (
    <>
      <circle cx="11" cy="11" r="6" />
      <path d="m16 16 4 4" />
    </>
  ),
  sparkle: (
    <>
      <path d="m12 3 1.6 5.4L19 10l-5.4 1.6L12 17l-1.6-5.4L5 10l5.4-1.6z" />
      <path d="m19 16 .6 2.4L22 19l-2.4.6L19 22l-.6-2.4L16 19l2.4-.6z" />
    </>
  ),
  trash: (
    <>
      <path d="M5 7h14M9 7V4h6v3M8 7l1 13h6l1-13" />
    </>
  ),
}

interface IconProps {
  name: keyof typeof paths
  size?: number
}

export function Icon({ name, size = 20 }: IconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {paths[name]}
    </svg>
  )
}
