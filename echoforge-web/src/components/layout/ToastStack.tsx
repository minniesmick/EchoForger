import { AnimatePresence, motion } from 'framer-motion'
import { type Toast } from '@/stores/useAppStore'
import { I } from '@/components/shared/Icons'

const toastVariants = {
  initial: { opacity: 0, x: 24, scale: 0.95 },
  animate: { opacity: 1, x: 0,  scale: 1    },
  exit:    { opacity: 0, x: 16, scale: 0.95 },
}
const toastTransition = {
  type: 'spring' as const,
  stiffness: 340,
  damping: 28,
}

export function ToastStack({ toasts }: { toasts: Toast[] }) {
  return (
    <div className="toast-stack">
      <AnimatePresence mode="sync">
        {toasts.map((t) => (
          <motion.div
            key={t.id}
            className={`toast ${t.kind ?? ''}`}
            layout
            variants={toastVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={toastTransition}
          >
            <span className="t-ico">
              {t.kind === 'success' ? <I.check />
               : t.kind === 'error' ? <I.warning />
               : <I.zap />}
            </span>
            <div className="t-body">
              <div className="t-title">{t.title}</div>
              {t.msg && <div className="t-msg">{t.msg}</div>}
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  )
}
