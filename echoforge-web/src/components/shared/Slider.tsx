import { useState } from 'react'

interface SliderProps {
  label:   string
  value:   number
  min:     number
  max:     number
  step:    number
  suffix?: string
}

export function Slider({ label, value, min, max, step, suffix }: SliderProps) {
  const [v, setV] = useState(value)
  const pct = ((v - min) / (max - min)) * 100

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
        <span style={{ fontSize: 12, color: 'var(--text-2)' }}>{label}</span>
        <span className="mono" style={{ fontSize: 12, color: 'var(--text)', fontVariantNumeric: 'tabular-nums' }}>
          {v.toFixed(2)}{suffix ?? ''}
        </span>
      </div>
      <div style={{ position: 'relative', height: 4, background: 'var(--surface-3)', borderRadius: 999 }}>
        <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: `${pct}%`, background: 'var(--violet)', borderRadius: 999 }} />
        <input
          type="range" min={min} max={max} step={step} value={v}
          onChange={(e) => setV(parseFloat(e.target.value))}
          style={{ position: 'absolute', inset: 0, opacity: 0, width: '100%', cursor: 'pointer', margin: 0 }}
        />
        <div style={{
          position: 'absolute', left: `${pct}%`, top: '50%',
          width: 12, height: 12, borderRadius: '50%',
          background: 'var(--violet-2)',
          transform: 'translate(-50%, -50%)',
          boxShadow: '0 0 0 3px var(--bg), 0 0 10px var(--violet-glow)',
          pointerEvents: 'none',
        }} />
      </div>
    </div>
  )
}
