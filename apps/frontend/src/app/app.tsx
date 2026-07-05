import { useState } from 'react'
import { LandingPage } from '../features/landing/landing-page'
import { WorkspacePage } from '../features/workspace/workspace-page'

export function App() {
  const [route, setRoute] = useState<'home' | 'workspace'>('home')
  const [openMatching, setOpenMatching] = useState(false)

  const openWorkspace = (withMatching: boolean) => {
    setOpenMatching(withMatching)
    setRoute('workspace')
  }

  if (route === 'home') {
    return (
      <LandingPage
        onExperiences={() => openWorkspace(false)}
        onMatching={() => openWorkspace(true)}
      />
    )
  }

  return (
    <WorkspacePage
      initialMatchingOpen={openMatching}
      onHome={() => setRoute('home')}
    />
  )
}
