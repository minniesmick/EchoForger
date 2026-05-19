import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { I } from '@/components/shared/Icons'
import type { ArchiveDoc } from '@/types'

// ── Mock data (Faz 8: GET /api/archive/search) ───────────────
const MOCK_DOCS: ArchiveDoc[] = [
  { id:'1', title:'Kickoff meeting — v0.7 release planning',        date:'May 18, 2026', dur:'3:17',    speakers:3, words:412,   snippet:'The big shift is moving Whisper inference off CPU and onto the local GPU node — should be roughly 6x faster. Both. The Settings panel exposes the model selector.' },
  { id:'2', title:'Interview · Dr. Thompson — voice cloning ethics', date:'May 15, 2026', dur:'42:08',   speakers:2, words:5841,  snippet:"When you train on someone's six seconds of audio, you're not just capturing their timbre — you're capturing prosody, emotional baseline, the small breath patterns. Consent has to scale with that." },
  { id:'3', title:'Podcast ep 042 — local-first AI',                date:'May 12, 2026', dur:'1:18:24', speakers:4, words:14820, snippet:"I think the future of voice models isn't in the cloud at all — it's on the device, with the user owning the weights. That's why we shipped Kokoro alongside XTTS." },
  { id:'4', title:'Product demo — Spanish narration draft',          date:'May 10, 2026', dur:'8:42',    speakers:1, words:1208,  snippet:'Bienvenidos a EchoForge, el estudio de voz local que pone los modelos en tus manos. Hoy vamos a recorrer las cuatro tuberías principales…' },
  { id:'5', title:'Standup · 2026-05-19',                           date:'May 19, 2026', dur:'14:22',   speakers:5, words:2104,  snippet:'Quick one from me — diarization toggle is wired up, just need to land the styling pass on the segment column collapse animation.' },
]

// ── Highlight search term in snippet ─────────────────────────
function Highlighted({ text, q }: { text: string; q: string }) {
  if (!q) return <>{text}</>
  const parts = text.split(new RegExp(`(${q})`, 'gi'))
  return (
    <>
      {parts.map((p, i) =>
        p.toLowerCase() === q.toLowerCase()
          ? <mark key={i}>{p}</mark>
          : p
      )}
    </>
  )
}

// ── Archive card ──────────────────────────────────────────────
function ArchiveCard({ doc, q }: { doc: ArchiveDoc; q: string }) {
  const [open, setOpen] = useState(false)

  return (
    <motion.div
      className="card archive-card glow"
      onClick={() => setOpen((o) => !o)}
      whileHover={{ y: -1 }}
      transition={{ duration: 0.14 }}
    >
      <div className="arc-head">
        <div>
          <div className="arc-title">{doc.title}</div>
          <div className="arc-meta">
            <span>{doc.date}</span><span>·</span>
            <span>{doc.dur}</span><span>·</span>
            <span><I.users style={{ width: 11, height: 11, verticalAlign: -2, marginRight: 3 }} />{doc.speakers}</span>
            <span>·</span>
            <span>{doc.words.toLocaleString()} words</span>
          </div>
        </div>
        <div style={{ display: 'flex', gap: 6, flexShrink: 0 }}>
          <span className="badge done"><span className="dot" />indexed</span>
          <button
            className="icon-btn"
            style={{ width: 26, height: 26 }}
            onClick={(e) => e.stopPropagation()}
          >
            <I.download />
          </button>
        </div>
      </div>

      <AnimatePresence initial={false}>
        <motion.div
          className={`arc-snippet${open ? ' open' : ''}`}
          animate={{ maxHeight: open ? 600 : 52 }}
          transition={{ duration: 0.28, ease: [0.16, 1, 0.3, 1] }}
          style={{ overflow: 'hidden' }}
        >
          <Highlighted text={doc.snippet} q={q} />
        </motion.div>
      </AnimatePresence>
    </motion.div>
  )
}

// ── Panel ─────────────────────────────────────────────────────
export default function PanelArchive() {
  const [q, setQ] = useState('whisper')

  const filtered = MOCK_DOCS

  return (
    <div className="panel-inner">
      <div className="panel-header">
        <div>
          <h1 className="panel-title">Archive</h1>
          <p className="panel-sub">
            {MOCK_DOCS.length} transcripts · indexed locally · semantic search via bge-small
          </p>
        </div>
      </div>

      {/* Search row */}
      <div className="search-row">
        <div className="search-input">
          <span className="search-ico"><I.search /></span>
          <input
            className="input"
            placeholder="Keyword search…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
          <span className="search-kbd">⌘K</span>
        </div>
        <div className="search-input">
          <span className="search-ico"><I.brain /></span>
          <input className="input" placeholder="Semantic search — describe what you remember…" />
        </div>
        <button className="btn ghost"><I.refresh /> Reindex</button>
      </div>

      {/* Results */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        <AnimatePresence>
          {filtered.map((d) => (
            <motion.div
              key={d.id}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
            >
              <ArchiveCard doc={d} q={q} />
            </motion.div>
          ))}
        </AnimatePresence>
        {filtered.length === 0 && (
          <div style={{ textAlign: 'center', padding: 40, color: 'var(--text-3)', fontSize: 13 }}>
            No transcripts match "<strong>{q}</strong>"
          </div>
        )}
      </div>
    </div>
  )
}
