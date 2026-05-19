import { motion } from 'framer-motion'

interface SwitchProps {
  on:       boolean
  onChange: (next: boolean) => void
  label?:   string
}

export function Switch({ on, onChange, label }: SwitchProps) {
  return (
    <div
      className={`switch${on ? ' on' : ''}`}
      onClick={() => onChange(!on)}
      role="switch"
      aria-checked={on}
      tabIndex={0}
      onKeyDown={(e) => (e.key === ' ' || e.key === 'Enter') && onChange(!on)}
    >
      <div className="switch-track">
        <motion.div
          className="switch-thumb"
          animate={{ left: on ? 15 : 1 }}
          transition={{ type: 'spring', stiffness: 400, damping: 28 }}
          style={{ position: 'absolute', top: 1 }}
        />
      </div>
      {label && <span className="switch-label">{label}</span>}
    </div>
  )
}
