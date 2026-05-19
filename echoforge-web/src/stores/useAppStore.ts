import { create } from 'zustand'

export type PanelId = 'dashboard' | 'stt' | 'tts' | 'ttt' | 'queue' | 'archive' | 'settings'
export type StatusKind = 'idle' | 'busy' | 'ready'
export type ToastKind  = 'success' | 'error' | 'info'

export interface Toast {
  id:       string
  kind?:    ToastKind
  title:    string
  msg?:     string
  leaving?: boolean
}

export interface VramState {
  used:  number
  total: number
}

interface AppState {
  // Navigation
  activePanel: PanelId
  setActivePanel: (id: PanelId) => void

  // Sidebar
  collapsed: boolean
  toggleCollapsed: () => void

  // System stats
  vram:   VramState
  gpu:    { util: number }
  status: StatusKind
  setVram:   (v: VramState) => void
  setStatus: (s: StatusKind) => void

  // Toasts
  toasts:    Toast[]
  pushToast: (t: Omit<Toast, 'id'>) => void
  _dismissToast: (id: string) => void
}

export const useAppStore = create<AppState>((set, get) => ({
  // ── Navigation ──────────────────────────────────────────
  activePanel: 'stt',
  setActivePanel: (id) => set({ activePanel: id }),

  // ── Sidebar ─────────────────────────────────────────────
  collapsed: false,
  toggleCollapsed: () => set((s) => ({ collapsed: !s.collapsed })),

  // ── System stats ────────────────────────────────────────
  vram:   { used: 6.2, total: 8 },   // RTX 3060 Ti: 8 GB
  gpu:    { util: 0 },
  status: 'idle',
  setVram:   (v) => set({ vram: v }),
  setStatus: (s) => set({ status: s }),

  // ── Toasts ──────────────────────────────────────────────
  toasts: [],
  pushToast: ({ kind, title, msg }) => {
    const id = Math.random().toString(36).slice(2)
    set((s) => ({ toasts: [...s.toasts, { id, kind, title, msg }] }))
    // Start exit animation after 3.6s, remove after 3.85s
    setTimeout(() => {
      set((s) => ({
        toasts: s.toasts.map((t) => (t.id === id ? { ...t, leaving: true } : t)),
      }))
      setTimeout(() => get()._dismissToast(id), 250)
    }, 3600)
  },
  _dismissToast: (id) =>
    set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),
}))

// ── Derived selectors (stable refs) ─────────────────────────
export const selectModelBadge = (state: AppState): string => {
  const map: Record<PanelId, string> = {
    dashboard: 'whisper-large-v3',
    stt:       'whisper-large-v3',
    tts:       'XTTSv2 · Aria',
    ttt:       'llama3.1:8b',
    queue:     'mixed',
    archive:   'bge-small (idx)',
    settings:  '—',
  }
  return map[state.activePanel]
}
