import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      // ── Reference CSS vars so Tailwind classes stay in sync ──
      colors: {
        bg:        'var(--bg)',
        'bg-2':    'var(--bg-2)',
        surface:   'var(--surface)',
        's-2':     'var(--surface-2)',
        's-3':     'var(--surface-3)',
        border:    'var(--border)',
        'border-2':'var(--border-2)',
        text:      'var(--text)',
        't-2':     'var(--text-2)',
        't-3':     'var(--text-3)',
        't-4':     'var(--text-4)',
        violet:    'var(--violet)',
        'violet-2':'var(--violet-2)',
        cyan:      'var(--cyan)',
        'cyan-2':  'var(--cyan-2)',
        green:     'var(--green)',
        red:       'var(--red)',
        amber:     'var(--amber)',
      },
      fontFamily: {
        sans: ["'Geist'", 'ui-sans-serif', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ["'Geist Mono'", 'ui-monospace', "'SF Mono'", 'Menlo', 'monospace'],
      },
      borderRadius: {
        card:  'var(--r-card)',
        input: 'var(--r-input)',
      },
      transitionTimingFunction: {
        spring:   'cubic-bezier(0.34, 1.56, 0.64, 1)',
        'ease-out-expo': 'cubic-bezier(0.16, 1, 0.3, 1)',
      },
      width: {
        sidebar:           'var(--sidebar-w)',
        'sidebar-collapsed':'var(--sidebar-w-collapsed)',
      },
      height: {
        topbar: 'var(--topbar-h)',
      },
    },
  },
  plugins: [],
} satisfies Config
