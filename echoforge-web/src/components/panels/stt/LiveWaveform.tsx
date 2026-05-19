import { useState, useEffect, useRef } from 'react'

const BAR_COUNT = 48

interface LiveWaveformProps {
  active: boolean
}

export function LiveWaveform({ active }: LiveWaveformProps) {
  const [bars, setBars]   = useState<number[]>(() => Array(BAR_COUNT).fill(4))
  const rafRef            = useRef<number>(0)
  const phaseRef          = useRef(0)

  useEffect(() => {
    if (!active) {
      setBars(Array(BAR_COUNT).fill(4))
      return
    }

    const tick = () => {
      phaseRef.current += 0.18
      const p = phaseRef.current
      setBars(Array.from({ length: BAR_COUNT }, (_, i) => {
        const base  = Math.sin(p + i * 0.32) * 0.5 + 0.5
        const noise = Math.random() * 0.7
        return Math.max(4, base * 24 + noise * 18)
      }))
      rafRef.current = requestAnimationFrame(tick)
    }

    rafRef.current = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(rafRef.current)
  }, [active])

  return (
    <div className="live-waveform">
      {bars.map((h, i) => (
        <div
          key={i}
          className="lw-bar"
          style={{ height: `${h}px`, opacity: active ? 1 : 0.3 }}
        />
      ))}
    </div>
  )
}
