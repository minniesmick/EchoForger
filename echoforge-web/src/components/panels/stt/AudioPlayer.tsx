import { useState, useEffect, useRef } from 'react'
import type { AudioFile } from '@/types'
import { I } from '@/components/shared/Icons'

// ── Frequency bar visualiser ─────────────────────────────────
const VIZ_BARS = 56

function PlayerViz({ playing }: { playing: boolean }) {
  const [bars, setBars] = useState<number[]>(() => Array(VIZ_BARS).fill(4))
  const rafRef          = useRef<number>(0)
  const phaseRef        = useRef(0)

  useEffect(() => {
    if (!playing) {
      cancelAnimationFrame(rafRef.current)
      setBars(Array(VIZ_BARS).fill(4))
      return
    }
    const tick = () => {
      phaseRef.current += 0.22
      const p = phaseRef.current
      setBars(Array.from({ length: VIZ_BARS }, (_, i) => {
        const n   = i / VIZ_BARS
        const env = Math.exp(-n * 1.3) * 0.9 + 0.1
        const wob = Math.sin(p * (1 + n * 0.3) + i * 0.4) * 0.5 + 0.5
        const v   = env * (0.45 + wob * 0.35 + Math.random() * 0.25)
        return Math.max(3, v * 34)
      }))
      rafRef.current = requestAnimationFrame(tick)
    }
    rafRef.current = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(rafRef.current)
  }, [playing])

  return (
    <div className={`player-viz${playing ? ' playing' : ' paused'}`}>
      {bars.map((h, i) => (
        <div key={i} className="vb" style={{ height: `${h}px` }} />
      ))}
    </div>
  )
}

// ── Time formatter ───────────────────────────────────────────
function fmt(t: number): string {
  const m = Math.floor(t / 60)
  const s = Math.floor(t % 60)
  return `${m}:${String(s).padStart(2, '0')}`
}

// ── AudioPlayer ──────────────────────────────────────────────
interface AudioPlayerProps {
  file:           AudioFile
  playing:        boolean
  setPlaying:     (v: boolean) => void
  currentTime:    number
  setCurrentTime: (v: number) => void
}

export function AudioPlayer({
  file, playing, setPlaying, currentTime, setCurrentTime,
}: AudioPlayerProps) {
  const seekRef  = useRef<HTMLDivElement>(null)
  const rafRef   = useRef<number>(0)
  const lastRef  = useRef<number>(0)

  // rAF-based playback clock
  useEffect(() => {
    if (!playing) { cancelAnimationFrame(rafRef.current); return }
    const tick = (now: number) => {
      const dt = (now - (lastRef.current || now)) / 1000
      lastRef.current = now
      setCurrentTime(prev => {
        const next = prev + dt
        if (next >= file.duration) { setPlaying(false); return file.duration }
        return next
      })
      rafRef.current = requestAnimationFrame(tick)
    }
    rafRef.current = requestAnimationFrame((now) => { lastRef.current = now; tick(now) })
    return () => cancelAnimationFrame(rafRef.current)
  }, [playing]) // eslint-disable-line react-hooks/exhaustive-deps

  const pct = Math.min(100, (currentTime / file.duration) * 100)

  const handleSeek = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!seekRef.current) return
    const r   = seekRef.current.getBoundingClientRect()
    const pct = Math.max(0, Math.min(1, (e.clientX - r.left) / r.width))
    setCurrentTime(pct * file.duration)
  }

  return (
    <div className="player">
      {/* Meta */}
      <div className="player-meta">
        <div className="pf-name mono">{file.name}</div>
        <div className="pf-sub">{file.sampleRate} · {fmt(file.duration)}</div>
      </div>

      {/* Controls */}
      <div className="player-controls">
        <button
          className="pc-btn"
          title="Skip back 10s"
          onClick={() => setCurrentTime(Math.max(0, currentTime - 10))}
        >
          <I.prev />
        </button>
        <button className="pc-btn pc-play" onClick={() => setPlaying(!playing)}>
          {playing ? <I.pause /> : <I.play />}
        </button>
        <button
          className="pc-btn"
          title="Skip forward 10s"
          onClick={() => setCurrentTime(Math.min(file.duration, currentTime + 10))}
        >
          <I.next />
        </button>
      </div>

      {/* Scrub bar */}
      <div className="player-scrub">
        <span>{fmt(currentTime)}</span>
        <div className="seek" ref={seekRef} onClick={handleSeek}>
          <div className="seek-fill" style={{ width: `${pct}%` }} />
          <div className="seek-thumb" style={{ left: `${pct}%` }} />
        </div>
        <span>{fmt(file.duration)}</span>
      </div>

      {/* Frequency viz */}
      <PlayerViz playing={playing} />

      {/* Volume (static for now) */}
      <div className="player-vol">
        <I.vol style={{ width: 14, height: 14 }} />
        <div className="vol-track">
          <div className="vol-fill" style={{ width: '72%' }} />
        </div>
      </div>
    </div>
  )
}
