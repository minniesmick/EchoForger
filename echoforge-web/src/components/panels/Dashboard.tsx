import type { VramState } from '@/stores/useAppStore'
import { I } from '@/components/shared/Icons'
import { useAppStore } from '@/stores/useAppStore'

// ── Mock data (Faz 8'de API'den gelecek) ─────────────────────
const ACTIVE_MODELS = [
  { name: 'whisper-large-v3',     kind: 'STT', vram: '3.1 GB', state: 'loaded' },
  { name: 'XTTSv2 · multilingual',kind: 'TTS', vram: '2.4 GB', state: 'loaded' },
  { name: 'llama3.1:8b-instruct', kind: 'LLM', vram: '0.0 GB', state: 'idle'   },
  { name: 'kokoro-v0.19',         kind: 'TTS', vram: '0.0 GB', state: 'idle'   },
]

const ACTIVITY = [
  { ico: 'mic',     text: <>Transcribed <span className="a-em">kickoff_meeting.wav</span> — 12 segments</>,  time: '2 min ago'  },
  { ico: 'speaker', text: <>Generated TTS for <span className="a-em">welcome_narration.txt</span></>,         time: '14 min ago' },
  { ico: 'chat',    text: <>LLM session with <span className="a-em">llama3.1:8b</span> — 4.2k tokens</>,     time: '38 min ago' },
  { ico: 'pipe',    text: <>STS pipeline ran <span className="a-em">3 files</span> end-to-end</>,             time: '1 hr ago'   },
  { ico: 'mic',     text: <>Transcribed <span className="a-em">interview_03.mp3</span> — 88 segments</>,     time: '2 hr ago'   },
  { ico: 'archive', text: <>Indexed <span className="a-em">7 transcripts</span> in archive</>,               time: '3 hr ago'   },
]

const QUICK_START = [
  { icon: I.mic,     label: 'Transcribe file',  sub: 'Whisper · local',  panel: 'stt'  },
  { icon: I.speaker, label: 'Generate speech',  sub: 'XTTSv2 · clone',  panel: 'tts'  },
  { icon: I.pipe,    label: 'STS pipeline',     sub: 'STT → TTS auto',  panel: 'stt'  },
  { icon: I.chat,    label: 'Chat with LLM',    sub: 'Ollama · stream',  panel: 'ttt'  },
] as const

// ── GPU ring ──────────────────────────────────────────────────
function GpuRing({ vram }: { vram: VramState }) {
  const pct     = (vram.used / vram.total) * 100
  const ringCirc = 2 * Math.PI * 42
  const ringOff  = ringCirc * (1 - pct / 100)

  return (
    <div className="gpu-ring">
      <svg viewBox="0 0 100 100">
        <defs>
          <linearGradient id="gpuGrad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#7c3aed" />
            <stop offset="100%" stopColor="#06b6d4" />
          </linearGradient>
        </defs>
        <circle className="gp-bg" cx="50" cy="50" r="42" fill="none" strokeWidth="8" />
        <circle
          className="gp-fg" cx="50" cy="50" r="42" fill="none" strokeWidth="8"
          strokeDasharray={ringCirc} strokeDashoffset={ringOff}
        />
      </svg>
      <div className="gp-text">{pct.toFixed(0)}%</div>
    </div>
  )
}

// ── Activity icon ─────────────────────────────────────────────
function ActivityIcon({ ico }: { ico: string }) {
  const s = { width: 14, height: 14 }
  switch (ico) {
    case 'mic':     return <I.mic     {...s} />
    case 'speaker': return <I.speaker {...s} />
    case 'chat':    return <I.chat    {...s} />
    case 'pipe':    return <I.pipe    {...s} />
    default:        return <I.archive {...s} />
  }
}

// ── Panel ─────────────────────────────────────────────────────
interface DashboardProps { vram: VramState }

export default function PanelDashboard({ vram }: DashboardProps) {
  const setActivePanel = useAppStore((s) => s.setActivePanel)

  return (
    <div className="panel-inner">
      <div className="panel-header">
        <div>
          <h1 className="panel-title">Dashboard</h1>
          <p className="panel-sub">System health · active models · recent pipeline activity</p>
        </div>
        <div className="panel-actions">
          <button className="btn ghost sm"><I.refresh /> Refresh</button>
          <button className="btn primary"><I.zap /> Run pipeline</button>
        </div>
      </div>

      <div className="dash-grid">
        {/* Metrics */}
        {[
          { label: 'Files transcribed', value: '1,284', sub: <><span className="m-trend up">+18 today</span> · 38 this week</> },
          { label: 'TTS minutes',       value: <>421<span style={{ fontSize: 18, color: 'var(--text-3)', marginLeft: 4 }}>m</span></>, sub: <><span className="m-trend up">+12.4m today</span></> },
          { label: 'LLM tokens',        value: <>2.41<span style={{ fontSize: 18, color: 'var(--text-3)', marginLeft: 4 }}>M</span></>, sub: 'in/out · all local' },
          { label: 'Avg STT WER',       value: <>4.2<span style={{ fontSize: 18, color: 'var(--text-3)', marginLeft: 4 }}>%</span></>,  sub: <><span className="m-trend down">−0.6%</span> · large-v3</> },
        ].map((m, i) => (
          <div key={i} className="card card-pad col-3 metric">
            <span className="m-label">{m.label}</span>
            <span className="m-value">{m.value}</span>
            <span className="m-sub">{m.sub}</span>
          </div>
        ))}

        {/* GPU card */}
        <div className="card card-pad col-7">
          <div className="card-title">GPU · RTX 3060 Ti · 8 GB</div>
          <div className="gpu-card">
            <GpuRing vram={vram} />
            <div className="gpu-stats">
              {[
                ['VRAM Used', `${vram.used.toFixed(1)} GB`],
                ['VRAM Free', `${(vram.total - vram.used).toFixed(1)} GB`],
                ['GPU Util',  '—'],
                ['Temp',      '—'],
                ['Power',     '—'],
                ['CUDA',      '11.8'],
              ].map(([l, v]) => (
                <div key={l} className="gs-row">
                  <div className="l">{l}</div>
                  <div className="v">{v}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Active models */}
        <div className="card col-5">
          <div className="card-pad" style={{ paddingBottom: 0 }}>
            <div className="card-title">Active models</div>
          </div>
          {ACTIVE_MODELS.map((m) => (
            <div key={m.name} className="model-row">
              <div className="m-ico">
                {m.kind === 'STT' ? <I.mic /> : m.kind === 'TTS' ? <I.speaker /> : <I.brain />}
              </div>
              <div>
                <div className="m-name mono">{m.name}</div>
                <div className="m-meta">
                  {m.kind} ·{' '}
                  {m.state === 'loaded'
                    ? <span style={{ color: 'var(--green)' }}>loaded</span>
                    : <span style={{ color: 'var(--text-4)' }}>idle</span>}
                </div>
              </div>
              <div className="m-vram">{m.vram}</div>
              <button className="icon-btn"><I.more /></button>
            </div>
          ))}
        </div>

        {/* Recent activity */}
        <div className="card col-7">
          <div className="card-pad" style={{ paddingBottom: 0, display: 'flex', justifyContent: 'space-between' }}>
            <div className="card-title">Recent activity</div>
            <span style={{ fontSize: 11, color: 'var(--text-3)', cursor: 'pointer' }}>View all →</span>
          </div>
          {ACTIVITY.map((a, i) => (
            <div key={i} className="activity-row">
              <div className="a-icon"><ActivityIcon ico={a.ico} /></div>
              <div className="a-text">{a.text}</div>
              <span className="badge done"><span className="dot" />ok</span>
              <span className="a-time">{a.time}</span>
            </div>
          ))}
        </div>

        {/* Quick start */}
        <div className="card card-pad col-5 glow" style={{
          background: 'linear-gradient(135deg, rgba(124,58,237,0.08) 0%, var(--surface) 60%)',
        }}>
          <div className="card-title">Quick start</div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
            {QUICK_START.map((qs) => (
              <div
                key={qs.label}
                className="card"
                style={{ padding: 12, cursor: 'pointer', background: 'var(--surface-2)' }}
                onClick={() => setActivePanel(qs.panel as any)}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <qs.icon style={{ width: 14, height: 14, color: 'var(--violet-2)' }} />
                  <div style={{ fontSize: 12, fontWeight: 500 }}>{qs.label}</div>
                </div>
                <div style={{ fontSize: 10.5, color: 'var(--text-3)', marginTop: 4 }}>{qs.sub}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
