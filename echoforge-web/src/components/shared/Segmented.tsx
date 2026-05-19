import { useRef, useEffect, useState } from 'react'
import { motion } from 'framer-motion'

interface Option {
  value: string
  label: string
  icon?:  (p: React.SVGProps<SVGSVGElement>) => JSX.Element
}

interface SegmentedProps {
  options:    Option[]
  value:      string
  onChange:   (v: string) => void
  stsAccent?: boolean
}

export function Segmented({ options, value, onChange, stsAccent }: SegmentedProps) {
  const wrapRef = useRef<HTMLDivElement>(null)
  const [thumb, setThumb] = useState({ left: 3, width: 0 })

  useEffect(() => {
    if (!wrapRef.current) return
    const idx  = options.findIndex((o) => o.value === value)
    const btns = wrapRef.current.querySelectorAll<HTMLButtonElement>('button')
    const btn  = btns[idx]
    if (!btn) return
    const r  = btn.getBoundingClientRect()
    const pr = wrapRef.current.getBoundingClientRect()
    setThumb({ left: r.left - pr.left, width: r.width })
  }, [value, options])

  const isSts = stsAccent && value === options[1]?.value

  return (
    <div
      ref={wrapRef}
      className={`segmented${isSts ? ' sts-active' : ''}`}
    >
      <motion.div
        className="seg-thumb"
        animate={{ left: thumb.left, width: thumb.width }}
        transition={{ type: 'spring', stiffness: 340, damping: 30 }}
        style={{ position: 'absolute' }}
      />
      {options.map((o) => {
        const Icon = o.icon
        return (
          <button
            key={o.value}
            className={value === o.value ? 'active' : ''}
            onClick={() => onChange(o.value)}
          >
            {Icon && <Icon style={{ width: 12, height: 12 }} />}
            {o.label}
          </button>
        )
      })}
    </div>
  )
}
