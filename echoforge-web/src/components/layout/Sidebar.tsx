import { motion, AnimatePresence } from 'framer-motion'
import { useAppStore, type PanelId } from '@/stores/useAppStore'
import { I } from '@/components/shared/Icons'

// ── Nav item config ──────────────────────────────────────────
interface NavItem {
  id:    PanelId
  label: string
  icon:  (p: React.SVGProps<SVGSVGElement>) => JSX.Element
  badge?: string
}

const NAV_ITEMS: NavItem[] = [
  { id: 'dashboard', label: 'Dashboard',   icon: I.home    },
  { id: 'stt',       label: 'STT',         icon: I.mic,    badge: '3' },
  { id: 'tts',       label: 'TTS Studio',  icon: I.speaker },
  { id: 'ttt',       label: 'TTT Chat',    icon: I.chat    },
  { id: 'queue',     label: 'Queue',       icon: I.queue,  badge: '7' },
  { id: 'archive',   label: 'Archive',     icon: I.archive },
  { id: 'settings',  label: 'Settings',    icon: I.settings},
]

// ── Animation variants ───────────────────────────────────────
const sidebarVariants = {
  expanded:  { width: 232 },
  collapsed: { width: 64  },
}
const sidebarTransition = {
  type: 'spring' as const,
  stiffness: 320,
  damping: 32,
  mass: 0.8,
}

const labelVariants = {
  expanded:  { opacity: 1, x: 0,   display: 'block'  },
  collapsed: { opacity: 0, x: -6,  transitionEnd: { display: 'none' } },
}
const labelTransition = { duration: 0.16, ease: [0.16, 1, 0.3, 1] as const }

const chevronVariants = {
  expanded:  { rotate: 0   },
  collapsed: { rotate: 180 },
}

// ── Nav item (memoizable) ────────────────────────────────────
function NavItemRow({ item, collapsed }: { item: NavItem; collapsed: boolean }) {
  const activePanel   = useAppStore((s) => s.activePanel)
  const setActivePanel = useAppStore((s) => s.setActivePanel)
  const isActive = activePanel === item.id
  const Icon = item.icon

  return (
    <motion.div
      className={`nav-item${isActive ? ' active' : ''}`}
      onClick={() => setActivePanel(item.id)}
      title={collapsed ? item.label : undefined}
      whileHover={{ x: collapsed ? 0 : 2 }}
      whileTap={{ scale: 0.97 }}
      transition={{ duration: 0.12 }}
    >
      <span className="nav-icon">
        <Icon />
      </span>

      <motion.span
        className="nav-label"
        variants={labelVariants}
        transition={labelTransition}
        style={{ overflow: 'hidden', whiteSpace: 'nowrap' }}
      >
        {item.label}
      </motion.span>

      <AnimatePresence>
        {item.badge && !collapsed && (
          <motion.span
            className="nav-badge"
            initial={{ opacity: 0, scale: 0.7 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.7 }}
            transition={{ duration: 0.15 }}
          >
            {item.badge}
          </motion.span>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

// ── Sidebar ──────────────────────────────────────────────────
export function Sidebar() {
  const collapsed      = useAppStore((s) => s.collapsed)
  const toggleCollapsed = useAppStore((s) => s.toggleCollapsed)
  const animState      = collapsed ? 'collapsed' : 'expanded'

  return (
    <motion.aside
      className="sidebar"
      variants={sidebarVariants}
      animate={animState}
      transition={sidebarTransition}
      style={{ overflow: 'hidden', gridRow: '1 / 3', gridColumn: 1 }}
    >
      {/* Brand */}
      <div className="sidebar-brand">
        <div className="brand-mark">
          <svg viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2"
            strokeLinecap="round" strokeLinejoin="round">
            <path d="M3 12h2l3-8 4 16 3-12 2 4h4"/>
          </svg>
        </div>
        <AnimatePresence>
          {!collapsed && (
            <motion.div
              className="brand-text"
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -8 }}
              transition={labelTransition}
            >
              EchoForge
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Nav */}
      <nav className="sidebar-nav">
        {NAV_ITEMS.map((item) => (
          <NavItemRow key={item.id} item={item} collapsed={collapsed} />
        ))}
      </nav>

      {/* Footer */}
      <div className="sidebar-footer">
        <div className="avatar">BA</div>
        <AnimatePresence>
          {!collapsed && (
            <motion.div
              className="user-meta"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.14 }}
            >
              <span className="u-name">Ben Alper</span>
              <span className="u-sub">Local · RTX 3060 Ti</span>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Collapse toggle */}
      <motion.button
        className="collapse-btn"
        onClick={toggleCollapsed}
        title={collapsed ? 'Expand' : 'Collapse'}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
      >
        <motion.span
          variants={chevronVariants}
          animate={animState}
          transition={{ type: 'spring', stiffness: 260, damping: 24 }}
          style={{ display: 'grid', placeItems: 'center' }}
        >
          <I.chevron style={{ width: 12, height: 12 }} />
        </motion.span>
      </motion.button>
    </motion.aside>
  )
}
