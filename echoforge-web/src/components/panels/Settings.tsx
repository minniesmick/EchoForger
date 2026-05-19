import { useState } from 'react'
import { Switch } from '@/components/shared/Switch'

// ── Setting row ───────────────────────────────────────────────
function SettingRow({ label, sub, children }: { label: string; sub: string; children: React.ReactNode }) {
  return (
    <div className="setting-row">
      <div>
        <div className="sr-label">{label}</div>
        <div className="sr-sub">{sub}</div>
      </div>
      <div className="sr-control">{children}</div>
    </div>
  )
}

function SwitchRow({ defaultOn }: { defaultOn: boolean }) {
  const [on, setOn] = useState(defaultOn)
  return <Switch on={on} onChange={setOn} />
}

// ── Sections ──────────────────────────────────────────────────
function SectionSTT() {
  return (
    <div className="card card-pad">
      <SettingRow label="Whisper model" sub="Default model loaded on startup. Larger = more accurate, more VRAM.">
        <select className="select" defaultValue="large-v3" style={{ width: 240 }}>
          <option value="tiny">tiny · 39M · 0.4 GB</option>
          <option value="base">base · 74M · 0.6 GB</option>
          <option value="small">small · 244M · 1.2 GB</option>
          <option value="medium">medium · 769M · 2.4 GB</option>
          <option value="large-v3">large-v3 · 1.55B · 3.1 GB</option>
        </select>
      </SettingRow>
      <SettingRow label="Silence threshold (dBFS)" sub="Below this, audio is treated as silence and skipped.">
        <input className="input" defaultValue="-40" style={{ width: 120, textAlign: 'right' }} />
      </SettingRow>
      <SettingRow label="Chunk size (seconds)" sub="Length of each Whisper inference chunk. 30s is the model default.">
        <input className="input" defaultValue="30" style={{ width: 120, textAlign: 'right' }} />
      </SettingRow>
      <SettingRow label="VAD filter" sub="Apply Silero VAD before transcription. Improves long-file accuracy.">
        <SwitchRow defaultOn />
      </SettingRow>
      <SettingRow label="Speaker diarization (default)" sub="Run pyannote 3.1 diarization on every transcript.">
        <SwitchRow defaultOn />
      </SettingRow>
    </div>
  )
}

function SectionTTS() {
  return (
    <div className="card card-pad">
      <SettingRow label="Model directory" sub="Where local TTS model weights are stored.">
        <input className="input mono" defaultValue="D:\AI_Ortak_Venv\models\tts" />
      </SettingRow>
      <SettingRow label="HuggingFace cache" sub="Shared HF cache for downloaded artifacts.">
        <input className="input mono" defaultValue="D:\AI_Ortak_Venv\.cache\huggingface" />
      </SettingRow>
      <SettingRow label="Default TTS model" sub="Used when not specified per-job.">
        <select className="select" defaultValue="xtts" style={{ width: 200 }}>
          <option value="xtts">XTTSv2 · multilingual</option>
          <option value="kokoro">Kokoro v0.19</option>
          <option value="hume">Hume TADA (cloud)</option>
        </select>
      </SettingRow>
      <SettingRow label="Output sample rate" sub="Forced resample of all TTS outputs.">
        <select className="select" defaultValue="24000" style={{ width: 140 }}>
          <option value="16000">16,000 Hz</option>
          <option value="22050">22,050 Hz</option>
          <option value="24000">24,000 Hz</option>
          <option value="44100">44,100 Hz</option>
          <option value="48000">48,000 Hz</option>
        </select>
      </SettingRow>
    </div>
  )
}

function SectionLLM() {
  return (
    <div className="card card-pad">
      <SettingRow label="Ollama base URL" sub="Local Ollama daemon. Default port 11434.">
        <input className="input mono" defaultValue="http://127.0.0.1:11434" />
      </SettingRow>
      <SettingRow label="Default Ollama model" sub="Pulled from Ollama on first use if missing.">
        <select className="select mono" defaultValue="llama3.1:8b-instruct-q4" style={{ width: 240 }}>
          <option>llama3.1:8b-instruct-q4</option>
          <option>llama3.1:70b-instruct-q4</option>
          <option>qwen2.5:7b-instruct</option>
          <option>mistral-nemo:12b-instruct</option>
        </select>
      </SettingRow>
      <SettingRow label="Gemini API key" sub="Stored in OS keychain. Never logged.">
        <input className="input mono" type="password" defaultValue="••••••••••••••••" style={{ width: 240 }} />
      </SettingRow>
      <SettingRow label="Streaming" sub="Stream tokens in TTT Chat panel.">
        <SwitchRow defaultOn />
      </SettingRow>
    </div>
  )
}

function SectionGeneral() {
  return (
    <div className="card card-pad">
      <SettingRow label="Output directory" sub="Where transcripts, exports, and TTS outputs go.">
        <input className="input mono" defaultValue="D:\AI_Ortak_Venv\EchoForge\output" />
      </SettingRow>
      <SettingRow label="Last mode" sub="Panel restored on app launch.">
        <select className="select" defaultValue="stt" style={{ width: 180 }}>
          <option value="dashboard">Dashboard</option>
          <option value="stt">STT</option>
          <option value="tts">TTS Studio</option>
          <option value="ttt">TTT Chat</option>
          <option value="queue">Queue</option>
        </select>
      </SettingRow>
      <SettingRow label="FastAPI host" sub="Backend URL for the web interface.">
        <input className="input mono" defaultValue="http://127.0.0.1:8000" />
      </SettingRow>
      <SettingRow label="Telemetry" sub="Anonymous crash reports only. Off by default.">
        <SwitchRow defaultOn={false} />
      </SettingRow>
      <SettingRow label="Theme" sub="Always dark — EchoForge is built for it.">
        <div className="segmented">
          <div className="seg-thumb" style={{ left: 3, width: 60 }} />
          <button className="active">Dark</button>
          <button disabled style={{ opacity: 0.4 }}>Light</button>
        </div>
      </SettingRow>
    </div>
  )
}

// ── Panel ─────────────────────────────────────────────────────
const SECTIONS = [
  { id: 'stt',     label: 'STT (Whisper)',  component: <SectionSTT />     },
  { id: 'tts',     label: 'TTS Models',     component: <SectionTTS />     },
  { id: 'llm',     label: 'LLM',            component: <SectionLLM />     },
  { id: 'general', label: 'General',        component: <SectionGeneral /> },
]

export default function PanelSettings() {
  const [section, setSection] = useState('stt')
  const active = SECTIONS.find((s) => s.id === section)

  return (
    <div className="panel-inner">
      <div className="panel-header">
        <div>
          <h1 className="panel-title">Settings</h1>
          <p className="panel-sub">
            Local configuration · changes save to{' '}
            <span className="mono" style={{ color: 'var(--text-2)' }}>~/.echoforge/config.toml</span>
          </p>
        </div>
      </div>

      <div className="settings-grid">
        <div className="settings-nav">
          {SECTIONS.map((s) => (
            <a
              key={s.id}
              className={section === s.id ? 'active' : ''}
              onClick={() => setSection(s.id)}
            >
              {s.label}
            </a>
          ))}
        </div>
        <div>{active?.component}</div>
      </div>
    </div>
  )
}
