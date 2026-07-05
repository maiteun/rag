import { Icon } from '../../components/ui/icon'

interface LandingPageProps {
  onExperiences: () => void
  onMatching: () => void
}

const actionBaseClass =
  'grid grid-cols-[auto_1fr_auto] items-center gap-3.5 rounded-[14px] border p-[18px] text-left transition-transform duration-300 hover:scale-102'

export function LandingPage({ onExperiences, onMatching }: LandingPageProps) {
  return (
    <div className="grid min-h-dvh grid-rows-[76px_1fr_64px] bg-[#f7f7f8] max-[760px]:grid-rows-[76px_1fr]">
      <header className="flex items-center border-b border-[#e7e7e9] px-8 max-[760px]:px-5">
        <Brand />
      </header>

      <main className="flex flex-col items-center justify-center px-6 pt-[72px] pb-[100px] text-center max-[760px]:pt-[50px]">
        <div>
          <span className="text-sm font-bold text-brand">
            경험을 모으고, 답변을 발견하세요
          </span>
          <h1 className="my-6 font-serif text-[clamp(50px,5.5vw,80px)] leading-[1.06] font-medium tracking-[-4px] max-[760px]:text-[44px] max-[760px]:tracking-[-2.5px]">
            내가 해온 일에서
            <br />
            <em className="font-medium">가장 좋은 답</em>을 찾습니다.
          </h1>
          <p className="mx-auto max-w-[590px] text-[17px] leading-[1.65] text-muted">
            흩어진 경험과 이력서를 정리하고, 지원 문항에 어울리는 경험을 빠르게
            찾아보세요.
          </p>
        </div>

        <div className="mt-9 grid w-full max-w-[760px] grid-cols-2 gap-[15px] max-[760px]:grid-cols-1">
          <LandingAction
            title="내 경험 둘러보기"
            description="정리된 경험과 근거 자료 확인"
            icon="archive"
            onClick={onExperiences}
          />
          <LandingAction
            title="문항과 경험 매칭하기"
            description="JD와 문항에 맞는 경험 추천"
            icon="sparkle"
            dark
            onClick={onMatching}
          />
        </div>
      </main>
    </div>
  )
}

function Brand() {
  return (
    <a
      className="text-xl font-extrabold tracking-[-.6px] text-ink no-underline"
      href="#"
      onClick={(event) => event.preventDefault()}
    >
      <span className="mr-2 inline-flex size-[25px] -rotate-[8deg] items-center justify-center rounded-[5px] bg-brand text-sm text-white">
        ㅁ
      </span>
      모람
    </a>
  )
}

interface LandingActionProps {
  title: string
  description: string
  icon: 'archive' | 'sparkle'
  dark?: boolean
  onClick: () => void
}

function LandingAction({ title, description, icon, dark = false, onClick }: LandingActionProps) {
  const colorClass = dark
    ? 'border-ink bg-ink text-white'
    : 'border-[#dedfe3] bg-white text-ink'

  return (
    <button className={`${actionBaseClass} ${colorClass}`} onClick={onClick}>
      <span
        className={`flex size-11 items-center justify-center rounded-[9px] ${
          dark ? 'bg-white/10 text-white' : 'bg-[#eff2ff] text-brand'
        }`}
      >
        <Icon name={icon} />
      </span>
      <span>
        <strong className="block text-[15px]">{title}</strong>
        <small className={`mt-[5px] block text-xs ${dark ? 'text-[#aaabb2]' : 'text-muted'}`}>
          {description}
        </small>
      </span>
      <Icon name="arrow" />
    </button>
  )
}
