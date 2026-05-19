import { motion, AnimatePresence } from 'framer-motion'
import type { Segment } from '@/types'

const SPK_LABELS: Record<number, string> = {
  1: 'Speaker 1',
  2: 'Speaker 2',
  3: 'Speaker 3',
}

function fmtMs(t: number): string {
  const m = Math.floor(t / 60)
  const s = (t % 60).toFixed(1)
  return `${String(m).padStart(2, '0')}:${s.padStart(4, '0')}`
}

interface TranscriptListProps {
  segments:  Segment[]
  diarize:   boolean
  activeIdx: number
  onJump:    (t: number) => void
  streaming?: boolean
}

// Stagger variants
const listVariants = {
  animate: { transition: { staggerChildren: 0.038 } },
}
const segVariants = {
  initial: { opacity: 0, y: 6 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.32, ease: [0.16, 1, 0.3, 1] } },
}

export function TranscriptList({
  segments, diarize, activeIdx, onJump, streaming = false,
}: TranscriptListProps) {
  return (
    <motion.div
      className={`transcript-list${diarize ? '' : ' no-diarize'}`}
      variants={listVariants}
      initial="initial"
      animate="animate"
    >
      <AnimatePresence initial={false}>
        {segments.map((s, i) => {
          const isActive = activeIdx === i
          return (
            <motion.div
				key={`${s.t}-${s.spk}`}
				className={`seg${isActive ? ' active' : ''}`}
				variants={segVariants}
				onClick={() => onJump(s.t)}
				layout="position"
			>
              {/* Timestamp */}
              <div className="seg-time mono">{fmtMs(s.t)}</div>

              {/* Speaker chip */}
              <div className={`seg-speaker s${s.spk}`}>
                <span className="sp-dot" />
                {SPK_LABELS[s.spk] ?? `Spk ${s.spk}`}
              </div>

              {/* Text */}
              <div className="seg-text">{s.text}</div>

              {/* Confidence */}
              <div className={`seg-conf mono${s.conf < 0.8 ? ' low' : ''}`}>
                {(s.conf * 100).toFixed(0)}%
              </div>
            </motion.div>
          )
        })}
      </AnimatePresence>

      {/* Typing indicator — shown while streaming */}
      <AnimatePresence>
        {streaming && (
          <motion.div
            className="transcript-typing"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <span /><span /><span />
            <span style={{ marginLeft: 8, fontSize: 11, color: 'var(--text-3)' }}>
              Whisper large-v3 · processing…
            </span>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
