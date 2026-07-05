import { useEffect, useRef, type ReactNode } from 'react'
import { Icon } from './icon'

type ModalSize = 'form' | 'detail' | 'resume'

interface ModalProps {
  title: string
  subtitle?: string
  size?: ModalSize
  children: ReactNode
  footer?: ReactNode
  onClose: () => void
}

const modalSizeClass: Record<ModalSize, string> = {
  form: 'h-[min(580px,calc(100dvh-48px))] w-[min(720px,calc(100vw-48px))]',
  detail: 'h-[min(680px,calc(100dvh-48px))] w-[min(880px,calc(100vw-48px))]',
  resume: 'h-[min(720px,calc(100dvh-48px))] w-[min(960px,calc(100vw-48px))]',
}

export function Modal({
  title,
  subtitle,
  size = 'detail',
  children,
  footer,
  onClose,
}: ModalProps) {
  const panel = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const previous = document.activeElement as HTMLElement | null
    const close = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose()
    }

    document.addEventListener('keydown', close)
    document.body.classList.add('has-modal')
    panel.current?.focus()

    return () => {
      document.removeEventListener('keydown', close)
      document.body.classList.remove('has-modal')
      previous?.focus()
    }
  }, [onClose])

  const closeOnBackdrop = (event: React.MouseEvent<HTMLDivElement>) => {
    if (event.target === event.currentTarget) onClose()
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-[rgba(20,21,28,.56)] p-6 max-[760px]:p-0"
      onMouseDown={closeOnBackdrop}
    >
      <div
        className={`grid grid-rows-[60px_minmax(0,1fr)_auto] overflow-hidden rounded-[15px] border border-[#dfe0e4] bg-white shadow-[0_28px_80px_rgba(15,18,30,.24)] outline-none max-[760px]:h-dvh max-[760px]:w-screen max-[760px]:rounded-none max-[760px]:border-0 ${modalSizeClass[size]}`}
        ref={panel}
        role="dialog"
        aria-modal="true"
        aria-labelledby="dialog-title"
        tabIndex={-1}
      >
        <header className="flex items-center justify-between border-b border-line px-6">
          <div>
            <h2 id="dialog-title" className="m-0 text-lg font-medium tracking-[-.3px]">
              {title}
            </h2>
            {subtitle && <p className="mt-1 mb-0 text-xs text-muted">{subtitle}</p>}
          </div>
          <button
            className="inline-flex items-center justify-center rounded-[7px] bg-transparent p-[7px] text-[#666976] hover:bg-[#f0f0f2] hover:text-ink"
            onClick={onClose}
            aria-label="닫기"
          >
            <Icon name="close" />
          </button>
        </header>
        <div className="min-h-0 overflow-auto">{children}</div>
        {footer && (
          <footer className="flex min-h-[70px] items-center justify-between px-6 py-3 max-[760px]:justify-end">
            {footer}
          </footer>
        )}
      </div>
    </div>
  )
}
