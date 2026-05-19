import { motion, useSpring, useTransform } from 'framer-motion'
import { useAppStore, type StatusKind, type VramState } from '@/stores/useAppStore'
import { I } from '@/components/shared/Icons'

const CRUMBS: Record<string, string> = {
  dashboard: 'Dashboard',
  stt:       'Speech to Text',
  tts:       'TTS Studio',
  ttt:       'TTT Chat',
  queue:     'Job Queue',
  archive:   'Archive',
  settings:  'Settings',
}

// ── Animated VRAM bar ────────────────────────────────────────
function VramMeter({ vram }: { vram: VramState }) {
  const pct = Math.min(100, Math.round((vram.used / vram.total) * 100))
  // Spring-smoothed fill width for buttery transition
  const springPct = useSpring(pct, { stiffness: 60, damping: 18 })
  const widthPct  = useTransform(springPct, (v) => `${v.toFixed(1)}%`)

  // Warn color above 85%
  const isHot = pct > 85

  return (
    <div className="vram-meter">
      <span className="vram-label">VRAM</span>
      <div className="vram-bar">
        <motion.div
          className="vram-fill"
          style={{
            width: widthPct,
            background: isHot
              ? 'linear-gradient(90deg, #ef4444, #f59e0b)'
              : 'linear-gradient(90deg, var(--violet), var(--cyan))',
          }}
        />
      </div>
      <span className="vram-value">
        {vram.used.toFixed(1)} / {vram.total} GB
      </span>
    </div>
  )
}

// ── Status dot ───────────────────────────────────────────────
function StatusDot({ status }: { status: StatusKind }) {
  return (
    <div className="topbar-chip">
      <span className={`dot ${status}`} />
      <span className="chip-label">Status</span>
      <span className="chip-value">
        {status === 'idle' ? 'Idle' : status === 'busy' ? 'Processing' : 'Ready'}
      </span>
    </div>
  )
}

// ── Topbar ───────────────────────────────────────────────────
export function Topbar({
  vram,
  gpu,
  status,
  modelBadge,
}: {
  vram:       VramState
  gpu:        { util: number }
  status:     StatusKind
  modelBadge: string
}) {
  const activePanel = useAppStore((s) => s.activePanel)

  return (
    <header className="topbar" style={{ gridColumn: 2, gridRow: 1 }}>
      {/* Breadcrumb */}
      <div className="topbar-title">
        <span>EchoForge</span>
        <span className="crumb-sep">/</span>
        <motion.span
          key={activePanel}
          className="crumb-current"
          initial={{ opacity: 0, y: 4 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.16 }}
        >
          {CRUMBS[activePanel]}
        </motion.span>
      </div>

      <div className="topbar-spacer" />

      {/* Status */}
      <StatusDot status={status} />

      {/* Active model */}
      <div className="topbar-chip">
        <I.chip style={{ width: 13, height: 13, color: 'var(--violet-2)' }} />
        <span className="chip-label">Active</span>
        <motion.span
          key={modelBadge}
          className="chip-value"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.2 }}
        >
          {modelBadge}
        </motion.span>
      </div>

      {/* GPU util */}
      {gpu.util > 0 && (
        <div className="topbar-chip">
          <I.cpu style={{ width: 13, height: 13, color: 'var(--cyan-2)' }} />
          <span className="chip-label">GPU</span>
          <span className="chip-value">{gpu.util}%</span>
        </div>
      )}

      {/* VRAM */}
      <VramMeter vram={vram} />

      <button className="icon-btn" title="Notifications">
        <I.bell />
      </button>
    </header>
  )
}
