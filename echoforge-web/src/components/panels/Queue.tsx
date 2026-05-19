import { motion } from 'framer-motion'
import { I } from '@/components/shared/Icons'
import type { QueueJob, JobState } from '@/types'

// ── Mock data (Faz 8: GET /api/queue) ────────────────────────
const MOCK_JOBS: QueueJob[] = [
  { id:'1', name:'podcast_ep_042.mp3',       kind:'STT',     size:'38.4 MB',  model:'whisper-large-v3',    state:'processing', progress:0.62, time:'2m 14s' },
  { id:'2', name:'narration_intro.txt',      kind:'TTS',     size:'1.2 KB',   model:'XTTSv2 · Aria',       state:'processing', progress:0.18, time:'24s'    },
  { id:'3', name:'standup_2026-05-19.wav',   kind:'STT+SUM', size:'22.1 MB',  model:'large-v3 + llama3.1', state:'waiting',    progress:0,    time:'—'      },
  { id:'4', name:'product_demo_es.mp4',      kind:'STT',     size:'142.0 MB', model:'whisper-medium',      state:'waiting',    progress:0,    time:'—'      },
  { id:'5', name:'interview_thompson.flac',  kind:'STS',     size:'94.8 MB',  model:'large-v3 → Kokoro',   state:'done',       progress:1,    time:'6m 02s' },
  { id:'6', name:'voiceover_chapter_3.txt',  kind:'TTS',     size:'8.4 KB',   model:'XTTSv2 · Kai',        state:'done',       progress:1,    time:'1m 11s' },
  { id:'7', name:'corrupt_audio_test.wav',   kind:'STT',     size:'0.4 MB',   model:'whisper-base',        state:'error',      progress:0.4,  time:'failed' },
]

// ── Badge colors per pipeline kind ───────────────────────────
function KindBadge({ kind }: { kind: string }) {
  const isSTS = kind === 'STS'
  const isTTS = kind === 'TTS'
  return (
    <span className="badge" style={{
      background:   isSTS ? 'rgba(124,58,237,0.1)'  : isTTS ? 'rgba(6,182,212,0.1)'  : 'var(--surface-2)',
      color:        isSTS ? 'var(--violet-2)'        : isTTS ? 'var(--cyan-2)'         : 'var(--text-2)',
      borderColor:  isSTS ? 'rgba(124,58,237,0.25)'  : isTTS ? 'rgba(6,182,212,0.25)'  : 'var(--border)',
    }}>
      {kind}
    </span>
  )
}

// ── Row icon ──────────────────────────────────────────────────
function RowIcon({ kind }: { kind: string }) {
  if (kind === 'STS')                                return <I.pipe    />
  if (kind.includes('TTS') && !kind.includes('STT')) return <I.speaker />
  return <I.audio />
}

// ── Progress bar ──────────────────────────────────────────────
function ProgressBar({ state, progress }: { state: JobState; progress: number }) {
  const fillClass = state === 'done' ? ' done' : state === 'error' ? ' error' : state === 'waiting' ? ' waiting' : ''
  return (
    <>
      <div className="q-progress">
        <motion.div
          className={`q-progress-fill${fillClass}`}
          initial={{ width: 0 }}
          animate={{ width: `${Math.max(progress, 0.02) * 100}%` }}
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
        />
      </div>
      <div style={{ fontSize: 11, color: 'var(--text-3)', marginTop: 4, fontVariantNumeric: 'tabular-nums' }}>
        {state === 'waiting' ? 'Queued' : `${Math.round(progress * 100)}%`}
      </div>
    </>
  )
}

// ── Panel ─────────────────────────────────────────────────────
export default function PanelQueue() {
  const processing = MOCK_JOBS.filter((j) => j.state === 'processing').length
  const waiting    = MOCK_JOBS.filter((j) => j.state === 'waiting').length
  const done       = MOCK_JOBS.filter((j) => j.state === 'done').length
  const errors     = MOCK_JOBS.filter((j) => j.state === 'error').length

  return (
    <div className="panel-inner">
      <div className="panel-header">
        <div>
          <h1 className="panel-title">Job Queue</h1>
          <p className="panel-sub">
            {MOCK_JOBS.length} jobs · {processing} processing · {waiting} waiting · {done} done · {errors} error
          </p>
        </div>
        <div className="panel-actions">
          <button className="btn ghost sm"><I.trash /> Clear done</button>
          <button className="btn ghost"><I.x /> Cancel all</button>
        </div>
      </div>

      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th style={{ width: '34%' }}>File</th>
              <th>Pipeline</th>
              <th>Model</th>
              <th style={{ width: '22%' }}>Progress</th>
              <th>Status</th>
              <th>Time</th>
              <th style={{ width: 50 }} />
            </tr>
          </thead>
          <tbody>
            {MOCK_JOBS.map((r) => (
              <tr key={r.id}>
                <td>
                  <div className="q-file">
                    <div className="q-file-ico"><RowIcon kind={r.kind} /></div>
                    <div>
                      <div className="q-file-name">{r.name}</div>
                      <div className="q-file-sub">{r.size}</div>
                    </div>
                  </div>
                </td>
                <td><KindBadge kind={r.kind} /></td>
                <td><span className="mono" style={{ fontSize: 12, color: 'var(--text-2)' }}>{r.model}</span></td>
                <td><ProgressBar state={r.state} progress={r.progress} /></td>
                <td><span className={`badge ${r.state}`}><span className="dot" />{r.state}</span></td>
                <td><span className="mono" style={{ fontSize: 12, color: 'var(--text-3)' }}>{r.time}</span></td>
                <td>
                  <button className="icon-btn" style={{ width: 26, height: 26 }}>
                    {r.state === 'done' ? <I.arrowRight /> : <I.x />}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
