import { useEffect, lazy, Suspense } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { useAppStore, selectModelBadge } from '@/stores/useAppStore'
import { Sidebar }    from '@/components/layout/Sidebar'
import { Topbar }     from '@/components/layout/Topbar'
import { ToastStack } from '@/components/layout/ToastStack'

// ── Lazy panel imports (code-split per panel) ────────────────
const PanelDashboard = lazy(() => import('@/components/panels/Dashboard'))
const PanelSTT       = lazy(() => import('@/components/panels/STT'))
const PanelTTS       = lazy(() => import('@/components/panels/TTS'))
const PanelTTT       = lazy(() => import('@/components/panels/TTT'))
const PanelQueue     = lazy(() => import('@/components/panels/Queue'))
const PanelArchive   = lazy(() => import('@/components/panels/Archive'))
const PanelSettings  = lazy(() => import('@/components/panels/Settings'))

// ── Panel transition variants ────────────────────────────────
const panelVariants = {
  initial: { opacity: 0, y: 10 },
  animate: { opacity: 1, y: 0  },
  exit:    { opacity: 0, y: -6 },
}
const panelTransition = {
  duration: 0.2,
  ease: [0.16, 1, 0.3, 1] as const,
}

// ── Panel loading skeleton ───────────────────────────────────
function PanelSkeleton() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16, height: '100%' }}>
      {[80, 180, 120].map((h, i) => (
        <div
          key={i}
          className="card"
          style={{
            height: h,
            animation: 'pulse 1.4s ease-in-out infinite',
            animationDelay: `${i * 120}ms`,
            opacity: 0.4,
          }}
        />
      ))}
    </div>
  )
}

// ── Ambient VRAM drift (simulated until WS connected) ───────
function useVramDrift() {
  const setVram = useAppStore((s) => s.setVram)
  const vram    = useAppStore((s) => s.vram)

  useEffect(() => {
    // Will be replaced by useVram() WebSocket hook in Faz 8
    const t = setInterval(() => {
      setVram({
        total: vram.total,
        used: Math.max(4, Math.min(7.5, vram.used + (Math.random() - 0.5) * 0.3)),
      })
    }, 2000)
    return () => clearInterval(t)
  }, []) // eslint-disable-line react-hooks/exhaustive-deps
}

// ── App ──────────────────────────────────────────────────────
export default function App() {
  const activePanel  = useAppStore((s) => s.activePanel)
  const collapsed    = useAppStore((s) => s.collapsed)
  const vram         = useAppStore((s) => s.vram)
  const gpu          = useAppStore((s) => s.gpu)
  const status       = useAppStore((s) => s.status)
  const toasts       = useAppStore((s) => s.toasts)
  const modelBadge   = useAppStore(selectModelBadge)
  const pushToast    = useAppStore((s) => s.pushToast)

  useVramDrift()

  // ── Render active panel ────────────────────────────────────
  const renderPanel = () => {
    switch (activePanel) {
      case 'dashboard': return <PanelDashboard vram={vram} />
      case 'stt':       return <PanelSTT       pushToast={pushToast} />
      case 'tts':       return <PanelTTS       pushToast={pushToast} />
      case 'ttt':       return <PanelTTT       pushToast={pushToast} />
      case 'queue':     return <PanelQueue />
      case 'archive':   return <PanelArchive />
      case 'settings':  return <PanelSettings />
    }
  }

  return (
    // Sidebar width driven by CSS vars; grid transition handled in CSS
    <div
      className={`app${collapsed ? ' collapsed' : ''}`}
      style={{ display: 'grid', height: '100vh' }}
    >
      <Sidebar />
      <Topbar
        vram={vram}
        gpu={gpu}
        status={status}
        modelBadge={modelBadge}
      />

      {/* Panel area — AnimatePresence drives mount/unmount transitions */}
      <AnimatePresence mode="wait" initial={false}>
        <motion.main
          key={activePanel}
          className="panel"
          variants={panelVariants}
          initial="initial"
          animate="animate"
          exit="exit"
          transition={panelTransition}
        >
          <Suspense fallback={<PanelSkeleton />}>
            {renderPanel()}
          </Suspense>
        </motion.main>
      </AnimatePresence>

      <ToastStack toasts={toasts} />
    </div>
  )
}
